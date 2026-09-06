"""Export evaluated R04 station chunks, retaining simple authored collision proxies."""
import bpy, bmesh, json, re
from pathlib import Path
from mathutils import Matrix, Vector
OUT=Path(__file__).resolve().parents[1]
FBX=OUT/'fbx'; FBX.mkdir(exist_ok=True)
source=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
manifest={'source':bpy.data.filepath,'units':'meters','materials':{},'chunks':[]}
collections=[c for c in bpy.data.collections if re.match(r'^(0[1-8]|1[0-4]|18)_',c.name)]
groups={}
for col in collections:
 for o in col.all_objects:
  if o.type not in {'MESH','FONT'}:continue
  if 'Temporary_Cut' in o.name:continue
  if col.name=='13_Roofs' and o.matrix_world.translation.x>25:continue
  key=col.name
  if col.name=='11_Doors':key=col.name+'_'+o.name
  groups.setdefault(key,[])
  if o not in groups[key]:groups[key].append(o)
scene=bpy.data.scenes.new('UE_Export_Temporary')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1

def record_material(m):
 if not m or m.name in manifest['materials']:return
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 row={'color':list(p.inputs['Base Color'].default_value if p else m.diffuse_color),'metallic':p.inputs['Metallic'].default_value if p else 0,'roughness':p.inputs['Roughness'].default_value if p else .6,'transmission':p.inputs['Transmission Weight'].default_value if p else 0,'textures':[]}
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:row['textures'].append({'name':n.image.name,'path':bpy.path.abspath(n.image.filepath)})
 manifest['materials'][m.name]=row

def copy_mesh(o,pivot,collision=False):
 if collision:
  me=o.data.copy()
  bm=bmesh.new();bm.from_mesh(me)
  result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  bmesh.ops.delete(bm,geom=result.get('geom_interior',[])+result.get('geom_unused',[]),context='VERTS')
  bm.to_mesh(me);bm.free()
 else:me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
 me.transform(Matrix.Translation(-pivot) @ o.matrix_world)
 ob=bpy.data.objects.new('export',me);scene.collection.objects.link(ob)
 if not collision and not me.uv_layers:
  uv=me.uv_layers.new(name='UVMap')
  for poly in me.polygons:
   axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in poly.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co
    uv.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
 for m in me.materials:record_material(m)
 return ob

for key,objects in groups.items():
 pivot=Vector((0,0,0))
 if key=='12_Gondola':pivot=bpy.data.objects['Gondola_MOVE_THIS'].matrix_world.translation.copy()
 meshes=[];colliders=[]
 name='SM_R04_'+re.sub('[^A-Za-z0-9_]','_',key)
 for o in objects:
  if o.get('export_geometry',True) and not o.hide_render:
   meshes.append(copy_mesh(o,pivot))
  if o.type=='MESH' and o.get('collision',False):colliders.append(copy_mesh(o,pivot,True))
 if not meshes:
  for o in colliders:bpy.data.objects.remove(o,do_unlink=True)
  continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.object.join();joined=bpy.context.object;joined.name=name
 for i,o in enumerate(colliders):o.name='UCX_'+name+'_'+str(i).zfill(3);o.select_set(True)
 bpy.context.view_layer.update()
 pts=[joined.matrix_world @ Vector(p) for p in joined.bound_box]
 row={'name':name,'collection':key,'pivot':list(pivot),'bounds_min':[min(p[i] for p in pts) for i in range(3)],'bounds_max':[max(p[i] for p in pts) for i in range(3)],'polygons':len(joined.data.polygons),'collision_hulls':len(colliders),'materials':[m.name if m else '' for m in joined.data.materials]}
 bpy.ops.export_scene.fbx(filepath=str(FBX/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=False,mesh_smooth_type='FACE',bake_anim=False,add_leaf_bones=False)
 manifest['chunks'].append(row)
 for o in [joined]+colliders:bpy.data.objects.remove(o,do_unlink=True)
 print('EXPORTED',name,flush=True)

bpy.ops.mesh.primitive_cube_add(size=1,location=(.5,1,1.5))
probe=bpy.context.object;probe.name='SM_R04_OrientationProbe';probe.scale=(1,2,3)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.export_scene.fbx(filepath=str(FBX/'SM_R04_OrientationProbe.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
(OUT/'export_manifest.json').write_text(json.dumps(manifest,indent=2))
print('EXPORT_COMPLETE',len(manifest['chunks']),flush=True)
