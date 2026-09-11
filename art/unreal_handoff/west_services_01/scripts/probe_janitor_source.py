import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];d=json.loads((P/'exports.json').read_text());bpy.ops.wm.open_mainfile(filepath=d['source']);bpy.context.scene.frame_set(1);rows=[]
for ob in bpy.context.scene.objects:
 if ob.type not in ['MESH','FONT','CURVE'] or ob.name.startswith('SD'):continue
 bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(v[j] for v in bb) for j in range(3)];hi=[max(v[j] for v in bb) for j in range(3)]
 if lo[0]<-10.3 and hi[0]>-12 and lo[1]<-7 and hi[1]>-8.5 and lo[2]<6.5 and hi[2]>4.1:rows.append({'name':ob.name,'lo':lo,'hi':hi})
(P/'janitor_source_probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
