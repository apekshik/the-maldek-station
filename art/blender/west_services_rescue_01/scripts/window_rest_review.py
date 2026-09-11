"""Idempotently set the privacy blind's intended rest state and refresh affected views."""
import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; O=Vector((-37.45,0,4.6))
for name in ['Maldek_Rescue_Hut_Editable.blend','Maldek_Rescue_Hut_Fitted_Review.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(P/name)); o=bpy.data.objects['WSR_Privacy_blind_fabric']; o.data.shape_keys.key_blocks['Lowered'].value=0.0; bpy.context.view_layer.update(); bpy.ops.wm.save_as_mainfile(filepath=str(P/name))
S=bpy.context.scene;cam=S.camera; d=cam.data
views=[('01_Porch_closed',(7.8,.4,1.68),(5.85,2.50,1.35),1,20),('02_Porch_open',(7.65,2.05,1.65),(2.9,2.35,1.1),40,23),('03_Inside_door',(3.2,2.1,1.65),(5.9,2.6,1.3),1,26),('05_Cupboards_open',(3.2,2.3,1.65),(.49,2.0,1.05),80,21),('06_Stretcher_folded',(4.0,2.6,1.65),(3.07,.45,1.73),1,35),('07_Stretcher_deployed',(5.2,4.0,2.15),(3.8,2.25,.55),40,26),('09_Window_inside',(4.4,3.0,1.68),(5.86,3.9,1.53),1,35),('11_Radio_heater',(3.30,2.7,1.64),(4.23,4.62,1.04),1,28)]
for n,p,t,f,l in views:
 S.frame_set(f); cam.location=O+Vector(p);cam.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler();d.type='PERSP';d.lens=l;S.render.filepath=str(P/'previews'/f'{n}.png');bpy.ops.render.render(write_still=True)
print('BLIND REST AND AFFECTED REVIEWS COMPLETE')


