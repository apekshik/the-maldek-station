"""Measure shell continuity and apertures; export and independently reimport FBX."""
import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
s=bpy.context.scene;source=bpy.data.collections['VF01_Control_Room'];deps=bpy.context.evaluated_depsgraph_get()
shell=[o for o in source.objects if o.name.startswith(('Insulated_wall_core','Closed_roof_slab','Interior_ceiling'))]
verts=[];faces=[]
for o in shell:
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps));k=len(verts);verts.extend([o.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(k+i for i in p.vertices) for p in me.polygons]);bpy.data.meshes.remove(me)
tree=BVHTree.FromPolygons(verts,faces)
checks=[]
def ray(label,p,d,length,want):
 hit=tree.ray_cast(Vector(p),Vector(d),length)[0] is not None;checks.append({'check':label,'passed':hit==want})
# Front doorway and west shared doorway are sampled inside the original opening.
for i in range(11):
 for j in range(12):
  ray('front doorway',(3.65+i*.11,4.5,.1+j*.2),(0,-1,0),1,False)
  ray('west doorway',(-.5,1.45+i*.11,.1+j*.2),(1,0,0),1,False)
for i in range(29):
 for z in [1.05,1.7,2.35]:ray('window aperture',(.45+i*.1,4.5,z),(0,-1,0),1,False)
# Continuous full-height solid side, and roof/wall junction from 3.08 through 3.20.
for y in [.1,.5,1,2,3,3.9]:
 for z in [.1,1,2,3.08,3.10,3.12,3.20]:ray('side enclosure',(5.5,y,z),(-1,0,0),1,True)
for x in [.1,.5,1,2,3,4,4.9]:
 for z in [3.08,3.10,3.12,3.20]:ray('front roof junction',(x,4.5,z),(0,-1,0),1,True)
report={'sampled_checks':len(checks),'failures':[c for c in checks if not c['passed']],'all_passed':all(c['passed'] for c in checks),'scope':'Shell rays only; not continuous player capsule sweeps.'}
assert report['all_passed'],report

# Evaluate modifiers into a separate export scene. Authored source remains editable.
es=bpy.data.scenes.new('Export_Temporary');es.unit_settings.system='METRIC';es.unit_settings.scale_length=1;bpy.context.window.scene=es
copies=[];materials={}
for o in source.objects:
 if o.type not in {'MESH','FONT'}:continue
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps));me.transform(o.matrix_world)
 # Metre-scale box projection is a base UV set, not a packed lightmap UV.
 uv=me.uv_layers.new(name='UV_Metres')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
 ob=bpy.data.objects.new(o.name,me);es.collection.objects.link(ob);copies.append(ob)
 for m in me.materials:
  if not m or m.name in materials:continue
  p=m.node_tree.nodes.get('Principled BSDF');materials[m.name]={'preview_color':list(m.diffuse_color),'metallic':p.inputs['Metallic'].default_value,'roughness':p.inputs['Roughness'].default_value,'procedural_shader_requires_Unreal_rebuild':True}
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='SM_VF01_Control_Sample'
def bounds(o):
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
bpy.context.view_layer.update();before=bounds(joined);render_verts=len(joined.data.vertices);render_faces=len(joined.data.polygons)
colliders=[]
def collision_cube(p,d):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=d;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.name=f'UCX_SM_VF01_Control_Sample_{len(colliders):03d}';colliders.append(o)
for o in source.objects:
 if o.name.startswith(('Insulated_wall_core','Concrete_floor','Closed_roof_slab')):
  lo,hi=bounds(o);collision_cube([(a+b)/2 for a,b in zip(lo,hi)],[b-a for a,b in zip(lo,hi)])
# Smooth walkable collision under the detailed bars, at matching top elevation.
collision_cube((2.5,4.99,-.025),(5,1.58,.05));collision_cube((5.75,2.9,-.025),(1.3,5.8,.05))
bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
for o in colliders:o.select_set(True)
fbx=OUT/'exports'/'SM_VF01_Control_Sample.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=False,mesh_smooth_type='FACE',bake_anim=False)
existing=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(fbx))
new=[o for o in bpy.data.objects if o not in existing];render=next(o for o in new if o.type=='MESH' and not o.name.startswith('UCX_'))
bpy.context.view_layer.update();after=bounds(render);error=max(abs(a-b) for rowa,rowb in zip(before,after) for a,b in zip(rowa,rowb))
assert error<.0001,(before,after,error)
report.update({'fbx_roundtrip_bounds_error_m':error,'render_vertices':render_verts,'render_polygons':render_faces,'collision_hulls':len(colliders),'bounds_m':before,'materials':materials,'unreal_import_validated':False,'source_station_translation_m':[-8,-4,4],'deck_placement':'Proposed sample extension; reconcile with platform layout before replacing live assets.'})
(OUT/'verification_and_export.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='materials'}),flush=True)
