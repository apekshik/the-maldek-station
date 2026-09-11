import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; R=P.parent/'west_services_01'
f=R/'Maldek_West_Services_Blockout.blend'
assert hashlib.sha256(f.read_bytes()).hexdigest()==json.loads((R/'delivery.json').read_text())['sha256']
bpy.ops.wm.open_mainfile(filepath=str(f))
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]; return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
d={'scene':bpy.context.scene.name,'collections':{},'objects':{}}
for c in bpy.data.collections:
 if c.name.startswith('WS_'): d['collections'][c.name]=[o.name for o in c.all_objects]
for o in bpy.context.scene.objects:
 if o.name.startswith('WS_'): d['objects'][o.name]={'bounds':bounds(o),'type':o.type}
(P/'reference_inspection.json').write_text(json.dumps(d,indent=2))
print(json.dumps(d,indent=2))
