import bpy,sys,json
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Generator_Fuel_Refinement.blend'))
s=bpy.context.scene;s.cycles.samples=24;(OUT/'previews').mkdir(exist_ok=True)
req=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['01','02','03','04','05']
for cam in bpy.data.collections['VF08_90_Presentation'].objects:
 if cam.type!='CAMERA' or cam.name[:2] not in req:continue
 for o in bpy.data.collections['VF08_02_Removable_Roofs'].objects:o.hide_render=cam.name.startswith('05')
 # Cutaway view removes only front and east shell sections; whole-scene save remains intact.
 hidden=[]
 if cam.name.startswith('05'):
  for cn in ['VF08_01_Generator_Shell','VF08_03_Workshop']:
   for o in bpy.data.collections[cn].objects:
    pts=[o.matrix_world@Vector(v) for v in o.bound_box];center=sum(pts,Vector())/8
    if (center.y<-18.7 or center.x>36.8) and center.z>-.85: o.hide_render=True;hidden.append(o)
 s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{cam.name}.png');print('RENDER',cam.name,flush=True)
 bpy.ops.render.render(write_still=True)
 for o in hidden:o.hide_render=False
print('RENDERS_COMPLETE',flush=True)
