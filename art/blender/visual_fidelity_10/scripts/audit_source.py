import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out.parent/'visual_fidelity_09/Maldek_Service_Apron_Refinement.blend'))
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if 'Parking' in o.name or 'Car' in o.name or ('Terrain' in o.name):rows.append({'name':o.name,'bounds':[lo,hi],'materials':[m.name for m in o.data.materials if m],'collections':[c.name for c in o.users_collection]})
(out/'source_audit.json').write_text(json.dumps(rows,indent=2))
