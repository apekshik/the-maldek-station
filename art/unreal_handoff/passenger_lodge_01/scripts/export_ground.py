import bpy,json,sys,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];sys.path.insert(0,str(Path(__file__).parent))
from site_shape import height
source=REPO/'art/unreal_handoff/revision12/gorge/station_gorge.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects['SM_Station_Gorge_Terrain'];changed=[];outside=0
for v in ob.data.vertices:
 p=ob.matrix_world@v.co;z=height(p.z,p.x,p.y)
 if abs(z-p.z)>1e-6:
  assert (-33<p.x<-23.6 and -16.3<p.y<9.35) or (-9.6<p.x<-5.05 and -16.5<p.y<-7.2)
  changed.append({'index':v.index,'before':list(p),'after_z':z});p.z=z;v.co=ob.matrix_world.inverted()@p
ob.data.update();ob.name='SM_Lodge_Site_Ground'
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(OUT/'fbx/SM_Lodge_Site_Ground.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lodge_Site_Ground.blend'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
(OUT/'ground_changes.json').write_text(json.dumps({'source_sha256':source_hash,'changed':changed,'unchanged_vertices':len(ob.data.vertices)-len(changed),'outside_mask_changes':outside},indent=2))
print('GROUND_EXPORT',len(changed),flush=True)
