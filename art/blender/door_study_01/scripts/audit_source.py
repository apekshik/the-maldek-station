import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
source=OUT.parent/'visual_fidelity_10/Maldek_Parking_Arrival.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
rows=[]
for o in bpy.data.collections['VF06_Control'].objects:
 if any(t in o.name.lower() for t in ['jamb','reveal','header','door','threshold']):
  v=[o.matrix_world@Vector(p) for p in o.bound_box]
  rows.append({'name':o.name,'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]})
(OUT/'source_openings.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
