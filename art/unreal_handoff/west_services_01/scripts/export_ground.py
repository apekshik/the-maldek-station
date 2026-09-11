import bpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));from site_shape import height
src=P.parent/'passenger_lodge_01/Lodge_Site_Ground.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));ob=bpy.data.objects['SM_Lodge_Site_Ground'];changes=[]
for v in ob.data.vertices:
 p=ob.matrix_world@v.co;z=height(p.z,p.x,p.y)
 if abs(z-p.z)>1e-6:changes.append({'index':v.index,'before':list(p),'after_z':z});p.z=z;v.co=ob.matrix_world.inverted()@p
ob.data.update();ob.name='SM_WS_Site_Ground';bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(P/'fbx/SM_WS_Site_Ground.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'West_Site_Ground.blend'));(P/'ground_changes.json').write_text(json.dumps({'source':str(src),'source_sha256':sha,'changed':changes,'unchanged_vertices':len(ob.data.vertices)-len(changes)},indent=2));print('GROUND',len(changes))
