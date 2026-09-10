"""Export only fitted PLW assets, preserving assembly origins and instancing."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'windows/fbx';dest.mkdir(parents=True,exist_ok=True)
src=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.scene.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
assets=[];placements=[];seen={}
for index in [1,2]:
 c=bpy.data.collections[f'PLW_Window_{index:02d}'];obs=[x for x in c.all_objects if x.type=='MESH'];root=[-22.7 if index==1 else -15.5,4,4.9];groups={}
 for ob in obs:
  assert not ob.hide_render
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps),depsgraph=deps);me.transform(ob.matrix_world)
  for v in me.vertices:v.co-=Vector(root)
  assert len(me.materials)==1
  mat=me.materials[0].name;copy=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(copy);groups.setdefault(mat,[]).append((copy,ob.name))
 for mat,items in sorted(groups.items()):
  bpy.ops.object.select_all(action='DESELECT')
  for ob,_ in items:ob.select_set(True)
  bpy.context.view_layer.objects.active=items[0][0];bpy.ops.object.join();ob=bpy.context.object
  # Same library construction at two positions; compare geometry to share one mesh.
  signature=hashlib.sha256(json.dumps({'v':[[round(x,4) for x in v.co] for v in ob.data.vertices],'f':[list(p.vertices) for p in ob.data.polygons],'mat':mat}).encode()).hexdigest()
  name=seen.get(signature)
  if not name:
   name=f'SM_PLW_{len(assets):02d}';seen[signature]=name;ob.name=name
   bpy.ops.export_scene.fbx(filepath=str(dest/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
   lo=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];hi=[max(v.co[j] for v in ob.data.vertices) for j in range(3)]
   assets.append({'name':name,'material':mat,'lo':lo,'hi':hi,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'sha256':hashlib.sha256((dest/(name+'.fbx')).read_bytes()).hexdigest()})
  placements.append({'label':f'MIG_PLW_{index:02d}_{len(placements):02d}','mesh':name,'pivot':root,'sources':[n for _,n in items]})
  bpy.data.objects.remove(ob,do_unlink=True)
assert sum(len(r['sources']) for r in placements)==132
(OUT/'windows/exports.json').write_text(json.dumps({'source_sha256':sha,'assets':assets,'placements':placements,'units':'metres; engine mapping (-X,+Y,+Z)','mechanisms':'Both windows fixed; no animated objects exported'},indent=2))
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
print('WINDOW_EXPORT',len(assets),len(placements),flush=True)
