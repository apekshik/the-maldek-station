import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.context.scene;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if (lo[0]>-12 and hi[0]<-10 and lo[1]>-9.05 and hi[1]<-7.2 and hi[2]>5) or (o.name.startswith('PLK_') and ('Prep' in o.name or o.hide_render)):
  rows.append({'name':o.name,'lo':lo,'hi':hi,'hidden':o.hide_render,'collections':[c.name for c in o.users_collection]})
print(json.dumps(rows,indent=2))
