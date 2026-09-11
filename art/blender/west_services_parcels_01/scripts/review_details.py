"""Rerender detail shots from the saved fitted file without rebuilding or saving it."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];O=Vector((-37.45,-5,4.6));a=json.loads((P/'assembly.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Fitted_Review.blend'));s=bpy.context.scene;cam=s.camera;d=cam.data
shots=[('04_counter_reverse',(2.8,2.9,1.65),(5.22,3.86,1.23),28,40),('05_tag_station',(4.1,3.25,1.5),(5.1,3.79,1.04),44,40),('06_secure_closed',(2.32,2.70,1.6),(2.2,.65,1.1),37,1),('07_secure_open',(3.12,2.72,1.6),(2.10,.65,1.05),34,40),('08_window_closed',(4.18,3.5,1.65),(5.9,3.9,1.53),35,1)]
for name,p,target,lens,frame in shots:
 s.frame_set(frame);cam.location=Vector(p)+O;cam.rotation_euler=(Vector(target)+O-cam.location).to_track_quat('-Z','Y').to_euler();d.type='PERSP';d.lens=lens;s.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('DETAIL_REVIEW_COMPLETE')
