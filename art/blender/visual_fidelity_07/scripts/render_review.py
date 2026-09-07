import bpy,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Station_Cleanup.blend'))
s=bpy.context.scene;(OUT/'previews').mkdir(exist_ok=True)
cams=sorted([o for o in bpy.data.objects if o.type=='CAMERA'],key=lambda o:o.name)
req=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for cam in cams:
 if req and cam.name[:2] not in req:continue
 s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{cam.name}.png')
 print('RENDER',cam.name,flush=True);bpy.ops.render.render(write_still=True)
