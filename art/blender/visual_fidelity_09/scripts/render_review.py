import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Service_Apron_Refinement.blend'))
s=bpy.context.scene;(OUT/'previews').mkdir(exist_ok=True)
for n in ['01_Generator_and_Fuel','06_Water_Connection','07_Apron_Plan']:
 s.camera=bpy.data.objects[n];s.render.filepath=str(OUT/'previews'/f'{n}.png');print('RENDER',n,flush=True);bpy.ops.render.render(write_still=True)
print('RENDERS_COMPLETE',flush=True)
