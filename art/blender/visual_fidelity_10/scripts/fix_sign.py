import bpy,math
from pathlib import Path
out=Path(__file__).resolve().parents[1];p=out/'Maldek_Parking_Arrival.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
for o in bpy.data.collections['VF10_02_Parking_Furniture'].objects:
 if o.type=='FONT':
  o.rotation_euler=(math.pi/2,0,math.pi)
  if 'FOOTPATH' in o.data.body:o.data.body='<  FOOTPATH'
bpy.ops.wm.save_as_mainfile(filepath=str(p))
