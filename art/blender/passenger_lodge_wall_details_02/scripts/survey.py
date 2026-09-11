import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];S=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend');bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();pts=[o.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 if not pts:continue
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if hi[0]>-13 and lo[0]<-9.9 and hi[1]>-7.5 and lo[1]<1.5 and hi[2]>4:
  rows.append(dict(name=o.name,lo=lo,hi=hi,materials=[m.name for m in o.data.materials]))
(P/'survey.json').write_text(json.dumps(dict(source=str(S),source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),objects=rows),indent=2));print('survey',len(rows))
