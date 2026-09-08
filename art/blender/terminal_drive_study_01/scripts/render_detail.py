import bpy
from pathlib import Path
from mathutils import Vector
o=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(o/'Maldek_Terminal_Drive_Study.blend'))
s=bpy.context.scene;c=s.camera;c.location=(-8,-13,11);c.rotation_euler=(Vector((-1.5,0,7.4))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=8.8;s.render.filepath=str(o/'drive_detail.png');bpy.ops.render.render(write_still=True)
