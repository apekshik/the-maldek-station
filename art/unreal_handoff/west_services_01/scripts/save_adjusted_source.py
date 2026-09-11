import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];d=json.loads((P/'exports.json').read_text());bpy.ops.wm.open_mainfile(filepath=d['source']);s=bpy.context.scene;s.name='Station_Engine_Adjusted';s.frame_set(1)
for n in d['integration_repairs']['shelf_objects']:bpy.data.objects[n].location.x+=d['integration_repairs']['shelf_shift_x_m']
for n in d['integration_repairs']['nonblocking_hardware']:bpy.data.objects[n]['Unreal_player_collision']='None; mating seal or small hardware'
bpy.data.objects['WSE_Engine_cover_hinge']['Unreal_open_angle_degrees']=100
ob=bpy.data.objects['WSE_Fuel_supply'];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
for v in ob.data.vertices:
 p=ob.matrix_world@v.co;p.y+=.55*max(0,min(1,(p.z-1.82)/.24));v.co=inv@p
bpy.data.objects['WSP_Door_hinge']['Unreal_hinge_collision_inset_m']=.025
bpy.data.objects['WSP_Door_hinge']['Unreal_latch_collision_inset_m']=.02
s['integration_manifest']=str(P/'exports.json');bpy.ops.wm.save_as_mainfile(filepath=str(P/'WestServices_EngineAdjusted.blend'))
