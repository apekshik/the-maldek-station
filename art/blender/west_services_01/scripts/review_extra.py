import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_West_Services_Blockout.blend'))
s=bpy.data.scenes['West_Services_Combined'];bpy.context.window.scene=s
c=bpy.data.collections['WS_REVIEW_ONLY']
for n,pos,target,lens in [('06_Porch_eye',(-28.4,-7.1,5.7),(-32.5,.2,5.7),22),('07_Power_inside',(-36.5,3.7,2.85),(-34.4,-2,2.0),22)]:
 d=bpy.data.cameras.new('WS_'+n);o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.camera=o;s.render.filepath=str(OUT/'previews'/f'{n}.png');bpy.ops.render.render(write_still=True)
