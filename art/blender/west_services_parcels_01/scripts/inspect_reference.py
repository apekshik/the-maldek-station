import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'west_services_01/Maldek_West_Services_Blockout.blend'))
s=bpy.data.scenes['West_Services_Combined'];bpy.context.window.scene=s
r={}
for cn in ['WS_PARCELS_PROXY','WS_SHARED_STRUCTURE']:
 r[cn]=[]
 for o in bpy.data.collections[cn].objects:
  if cn=='WS_SHARED_STRUCTURE' and not (o.name.startswith('WS_Upper') or 'PartyWall' in o.name):continue
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  r[cn].append({'name':o.name,'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'type':o.type})
(p/'reference_inspection.json').write_text(json.dumps(r,indent=2))
print('INSPECTED',s.name,len(s.objects),r['WS_PARCELS_PROXY'])
