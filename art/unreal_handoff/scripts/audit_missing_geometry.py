import bpy,json
from pathlib import Path
from mathutils import Vector
out={}
for c in bpy.data.collections:
 if c.name[:2] not in ['07','09','13','15']:continue
 rows=[]
 for o in c.all_objects:
  if o.type not in ['MESH','CURVE']:continue
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  rows.append({'name':o.name,'type':o.type,'hidden_render':o.hide_render,'export_geometry':o.get('export_geometry',True),'collision':o.get('collision',False),'location':list(o.matrix_world.translation),'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]})
 out[c.name]=rows
(Path(__file__).resolve().parents[1]/'missing_geometry_audit.json').write_text(json.dumps(out,indent=2))
