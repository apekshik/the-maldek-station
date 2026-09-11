import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/blender/west_services_power_01')
S=P.parent/'west_services_01'
d=json.loads((S/'delivery.json').read_text()); h=hashlib.sha256((S/d['blend']).read_bytes()).hexdigest(); assert h==d['sha256']
bpy.ops.wm.open_mainfile(filepath=str(S/d['blend']))
out={'hash':h,'scene':bpy.context.scene.name,'objects':[]}
for c in bpy.data.collections:
 if c.name.startswith('WS_'):
  for o in c.objects:
   if o.type=='MESH':
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    out['objects'].append({'collection':c.name,'name':o.name,'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]})
(P/'reference_inspection.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
