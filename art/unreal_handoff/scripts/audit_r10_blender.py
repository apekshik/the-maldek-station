import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'revision10';out.mkdir(exist_ok=True)
rows=[]
for c in bpy.data.collections:
 if not c.name.startswith(('01_','03_','06_','10_','13_')):continue
 for o in c.objects:
  if o.type!='MESH':continue
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'collection':c.name,'lo':[round(min(v[i] for v in bb),3) for i in range(3)],'hi':[round(max(v[i] for v in bb),3) for i in range(3)],'hidden':o.hide_render,'collision':bool(o.get('collision',False))})
(out/'blender_audit.json').write_text(json.dumps(rows,indent=2))
