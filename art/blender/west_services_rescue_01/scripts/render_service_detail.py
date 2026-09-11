import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Fitted_Review.blend'));S=bpy.context.scene;S.frame_set(1);c=S.camera
for name,pos,target,lens in [('09_Window_inside',(4.4,3.0,1.68),(5.86,3.9,1.53),35),('11_Radio_heater',(3.30,2.7,1.64),(4.23,4.62,1.04),28)]:
 p,t=Vector(pos),Vector(target);c.location=Vector((-37.45,0,4.6))+p;c.rotation_euler=(t-p).to_track_quat('-Z','Y').to_euler();c.data.type='PERSP';c.data.lens=lens;S.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
