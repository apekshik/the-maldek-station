"""Remove the six-millimetre cover overlap seen in glancing review close-ups.

build.py directly authors the corrected butt joints; this migration is retained
as repair evidence for the initial package review file.
"""
import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'))
s=bpy.data.scenes['PLD_Fitted_Doors'];bpy.context.window.scene=s;s.frame_set(1)
for key,H in [('ARRIVAL',2.3),('GONDOLA',2.3),('STAFF',2.2)]:
 for o in bpy.data.collections['PLD_'+key+'_Assembly'].objects:
  if 'Jamb_Cover' not in o.name:continue
  if min(v.co.z for v in o.data.vertices)<-.005:
   for v in o.data.vertices:v.co.z=H/2+(v.co.z-H/2)*H/(H+.012)
bpy.context.view_layer.update()
data=json.loads((OUT/'replacement_manifest.json').read_text())
for rec in data['objects']:rec['dimensions']=list(bpy.data.objects[rec['name']].dimensions)
(OUT/'replacement_manifest.json').write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'),compress=True)
