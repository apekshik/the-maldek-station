import bpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Police_Tape_Prototype.blend'))
s=bpy.context.scene;s.camera=bpy.data.objects['03_Contact_review']
s.render.resolution_x=960;s.render.resolution_y=540
s.cycles.samples=8;s.cycles.use_denoising=True
s.render.image_settings.file_format='PNG'
(out/'previews/motion_frames').mkdir(exist_ok=True)
s.render.filepath=str(out/'previews/motion_frames/frame_')
s.frame_step=2
bpy.ops.render.render(animation=True)
