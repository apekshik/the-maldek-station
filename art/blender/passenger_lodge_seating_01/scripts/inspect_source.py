import bpy,json,os
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
SRC=Path(os.environ.get('MALDEK_SOURCE_REPO','C:/Users/apek-anna/Developer/the-maldek-station'))/'art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
 if o.name.startswith(('FIT_Table_','FIT_Bench_')):
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],lo=[min(v[i] for v in vs) for i in range(3)],hi=[max(v[i] for v in vs) for i in range(3)]))
(OUT/'source_inventory.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows[:14],indent=2));print('TOTAL',len(rows))
