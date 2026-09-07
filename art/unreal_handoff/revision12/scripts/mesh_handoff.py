"""Blender-only evaluated mesh handoff helpers. Never writes the approved source."""
import bpy,math,json,hashlib,re
from pathlib import Path
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
EXPECTED='e2ce19363f35f7fbef1860f5d5591e53ccf0b97d989085153b631a82558724dd'
def slug(name):return re.sub('[^A-Za-z0-9_]','_',name)
def load_source():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED,'Approved VF07 source changed; re-audit first'
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
 bpy.context.view_layer.update()
 return bpy.context.scene,bpy.context.evaluated_depsgraph_get()
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def physical(name):
 n=name.lower()
 if any(w in n for w in ['gravel','parking']):return 'Gravel'
 if any(w in n for w in ['concrete','floor','ivory']) and not any(w in n for w in ['metal','gondola']):return 'Concrete'
 if any(w in n for w in ['timber','wood']):return 'Wood'
 if 'terrain' in n:return 'Soil'
 return 'Metal'
def collision_kind(o):
 n=o.name.lower()
 if o.name in {'Arrival_ground_approach','Service_road','Relay_outbound','Relay_return','Continuous_service_apron','R12_Forest_Approach_Aligned'}:return 'surface_prisms'
 if o.get('collision',False):return 'authored'
 if any(t in n for t in ['open_grating_tile','flush_steel_plate','floor','gravel_route','service_apron','flush_threshold']):return 'floor'
 if any(t in n for t in ['folded_corrugated','inner_lining','wall_panel','door_return','door_lintel','structural_corner','perimeter_beam','roof','ceiling','landing_support','deck_column','foundation_pier','tank_body','mattress','bed_base','desk_top','cabinet_body','control_console','control_seat','waiting_bench']):return 'solid'
 if any(t in n for t in ['tubular_guard','guard_post','handrail','toe_kick']):return 'guard'
 return None
class Handoff:
 def __init__(self,source,dependency_graph,folder):
  self.source=source;self.deps=dependency_graph;self.folder=OUT/folder;self.folder.mkdir(exist_ok=True)
  self.scene=bpy.data.scenes.new('R12_Export_Copy');self.scene.unit_settings.system='METRIC';self.scene.unit_settings.scale_length=1
  self.materials={};self.chunks=[];self.material_copies={}
 def material(self,m,exposure=None):
  key=m.name+('__'+exposure if exposure else '')
  if key not in self.materials:
   slot='UE_'+slug(key);copy=m.copy();copy.name=slot;self.material_copies[key]=copy
   p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
   self.materials[key]={'slot':slot,'source_material':m.name,'exposure':exposure,'physical_surface':physical(m.name),'glass':bool(p and p.inputs['Transmission Weight'].default_value>.5),'base_color':list(p.inputs['Base Color'].default_value if p else m.diffuse_color),'metallic':p.inputs['Metallic'].default_value if p else 0,'roughness':p.inputs['Roughness'].default_value if p else .6,'emission_color':list(p.inputs['Emission Color'].default_value) if p else [0,0,0,1],'emission_strength':p.inputs['Emission Strength'].default_value if p else 0}
  return self.material_copies[key]
 def chunk(self,name,objects,pivot=(0,0,0),extra_boxes=(),surface='Metal',role='solid',targets=(),exposure=None):
  pivot=Vector(pivot);verts=[];faces=[];uvs=[];normals=[];face_mats=[];mats=[];boxes=list(extra_boxes);sources=[]
  for o in sorted(objects,key=lambda o:o.name):
   if o.type not in {'MESH','CURVE','FONT'}:continue
   if not o.hide_render and o.get('export_geometry',True):
    ev=o.evaluated_get(self.deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=self.deps)
    if me:
     me.calc_loop_triangles();offset=len(verts);normal_matrix=o.matrix_world.to_3x3().inverted().transposed()
     verts.extend([tuple(o.matrix_world@v.co-pivot) for v in me.vertices])
     local_slots=[]
     for m in me.materials:
      if not m:raise RuntimeError('Missing source material: '+o.name)
      cm=self.material(m,exposure)
      if cm not in mats:mats.append(cm)
      local_slots.append(mats.index(cm))
     for tri in me.loop_triangles:
      faces.append(tuple(offset+i for i in tri.vertices));face_mats.append(local_slots[tri.material_index] if local_slots else 0)
      normal=(normal_matrix@tri.normal).normalized();axis=max(range(3),key=lambda i:abs(normal[i]))
      axes={0:(1,2),1:(0,2),2:(0,1)}[axis];sign=-1 if (axis==1 and normal.y>0) or (axis!=1 and normal[axis]<0) else 1
      for li in tri.loops:
       co=o.matrix_world@me.vertices[me.loops[li].vertex_index].co
       uvs.append(tuple(me.uv_layers.active.data[li].uv) if o.get('handoff_preserve_uv') and me.uv_layers.active else (sign*co[axes[0]]/8+.5,co[axes[1]]/8+.5))
       normals.append(tuple((normal_matrix@me.corner_normals[li].vector).normalized()))
     ev.to_mesh_clear();sources.append(o.name)
   kind=collision_kind(o) if role!='terrain' else None
   if kind=='surface_prisms':
    # Grade-following ribbon/apron collision. A single box would cover road bends,
    # change their elevation, and fill reserved grating/stair openings.
    o.data.calc_loop_triangles()
    for tri in o.data.loop_triangles:
     top=[o.matrix_world@o.data.vertices[j].co for j in tri.vertices]
     normal=(top[1]-top[0]).cross(top[2]-top[0]).normalized()
     if normal.z<.5:continue
     vertices=top+[v-Vector((0,0,.12)) for v in top]
     a=[min(v[i] for v in vertices) for i in range(3)];b=[max(v[i] for v in vertices) for i in range(3)]
     boxes.append({'min':a,'max':b,'vertices':[list(v) for v in vertices],'faces':[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],'source':o.name,'kind':kind})
    kind=None
   if kind:
    a,b=bounds(o)
    # One proxy per authored part, never a room- or assembly-wide hull.
    # Fill the reviewed grating tile only; its surrounding stairwell remains open.
    if kind=='floor' and 'grating_tile' in o.name.lower():
     a[0]-=.005;a[1]-=.005;b[0]+=.005;b[1]+=.005
    box={'min':a,'max':b,'source':o.name,'kind':kind}
    if kind!='floor':
     # Preserve orientation of narrow diagonal guards and authored hulls.
     # Blender's bound_box corner order is converted to our UCX face order.
     box['vertices']=[list(o.matrix_world@Vector(o.bound_box[j])) for j in [0,4,3,7,1,5,2,6]]
    if o.get('handoff_collision_vertices'):
     box['vertices']=json.loads(o['handoff_collision_vertices'])
     box['min']=[min(v[i] for v in box['vertices']) for i in range(3)]
     box['max']=[max(v[i] for v in box['vertices']) for i in range(3)]
    boxes.append(box)
  assert faces,('Empty export chunk',name)
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
  for m in mats:me.materials.append(m)
  if not mats:
   m=bpy.data.materials.new('UE_Probe');m.diffuse_color=(.8,.4,.05,1);me.materials.append(m)
  layer=me.uv_layers.new(name='SurfaceUV')
  for i,uv in enumerate(uvs):layer.data[i].uv=uv
  for i,p in enumerate(me.polygons):p.material_index=face_mats[i];p.use_smooth=True
  if normals:me.normals_split_custom_set(normals)
  ob=bpy.data.objects.new(name,me);self.scene.collection.objects.link(ob)
  colliders=[]
  for i,b in enumerate(boxes):
   a=Vector(b['min'])-pivot;z=Vector(b['max'])-pivot
   if min(z-a)<.0001:continue
   v=[tuple(Vector(p)-pivot) for p in b['vertices']] if 'vertices' in b else [(x,y,h) for h in [a.z,z.z] for y in [a.y,z.y] for x in [a.x,z.x]]
   cm=bpy.data.meshes.new('UCX');cm.from_pydata(v,[],b.get('faces',[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]))
   co=bpy.data.objects.new(f'UCX_{name}_{i:04d}',cm);self.scene.collection.objects.link(co);colliders.append(co)
  bpy.context.window.scene=self.scene;bpy.ops.object.select_all(action='DESELECT')
  ob.select_set(True);bpy.context.view_layer.objects.active=ob
  for c in colliders:c.select_set(True)
  file=self.folder/(name+'.fbx')
  bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=False,mesh_smooth_type='FACE',use_tspace=True,bake_anim=False,add_leaf_bones=False)
  rendered=[verts[i] for i in {j for f in faces for j in f}]
  render_bounds=[[min(v[i] for v in rendered) for i in range(3)],[max(v[i] for v in rendered) for i in range(3)]]
  row={'name':name,'file':str(file.relative_to(OUT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'sources':sources,'pivot':list(pivot),'bounds':render_bounds,'material_slots':[m.name for m in me.materials],'triangles':len(faces),'collision_boxes':boxes,'collision_hulls':len(colliders),'physical_surface':surface,'role':role,'nanite':role=='solid','replacement_targets':list(targets)}
  self.chunks.append(row)
  for c in colliders:c.hide_render=True;c.hide_set(True)
  bpy.context.window.scene=self.source
  print('EXPORTED',name,len(faces),len(colliders),flush=True)
  return row
 def save(self,name):
  manifest={'source':str(SOURCE),'source_sha256':EXPECTED,'units':'metres','texture_tile_metres':8,'axis_forward':'-Y','axis_up':'Z','placement':'FBX scene conversion once; audited station actor yaw 180. wp(x,y,z)=(origin.x-100*x,origin.y+100*y,origin.z+100*z).','materials':self.materials,'chunks':self.chunks}
  (OUT/(name+'.json')).write_text(json.dumps(manifest,indent=2))
  bpy.context.window.scene=self.scene;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')),copy=True)
  return manifest
