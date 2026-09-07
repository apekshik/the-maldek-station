import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/apek-anna/Developer/the-maldek-station')
bpy.ops.wm.open_mainfile(filepath=str(root/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'))
def bb(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
rows=[]
for c in bpy.data.collections:
 obs=list(c.objects)
 if any(w in c.name for w in ['Service','Generator','Maintenance','Fuel','Water']):
  rows.append({'collection':c.name,'objects':[{'name':o.name,'bounds':bb(o),'hidden':o.hide_render} for o in obs if o.type=='MESH']})
(root/'art/blender/visual_fidelity_08/source_audit.json').write_text(json.dumps(rows,indent=2))
print([(r['collection'],len(r['objects'])) for r in rows])
