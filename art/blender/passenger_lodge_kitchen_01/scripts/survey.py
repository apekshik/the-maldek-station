import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
 if o.name.startswith(('FIT_','PL03_')) and any(q in o.name.lower() for q in ['coffee','serving','prep','dry_store','urn','kettle','microwave','fridge','wash_sink','hand_basin','lost_property','menu']):
  p=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],lo=[min(v[i] for v in p) for i in range(3)],hi=[max(v[i] for v in p) for i in range(3)],matrix=[list(r) for r in o.matrix_world]))
(out/'source_survey.json').write_text(json.dumps(rows,indent=2))
print('Survey records:',len(rows))
