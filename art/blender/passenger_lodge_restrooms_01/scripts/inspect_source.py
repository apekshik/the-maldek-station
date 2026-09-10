import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
out=[]
for o in s.objects:
 if o.type=='MESH':
  v=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
  if lo[0]<-10 and hi[0]>-16.4 and lo[1]<-7.1 and hi[1]>-13.4 and hi[2]>4:
   out.append(dict(name=o.name,lo=lo,hi=hi,materials=[m.name for m in o.data.materials]))
(P/'source_inventory.json').write_text(json.dumps(out,indent=2))
