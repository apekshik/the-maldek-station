import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
 if o.type!='MESH' or not o.visible_get():continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in ps) for i in range(3)];hi=[max(v[i] for v in ps) for i in range(3)]
 if lo[0]<-26 and hi[0]>-43 and lo[1]<9 and hi[1]>-17:rows.append({'name':o.name,'lo':lo,'hi':hi})
(p/'survey.json').write_text(json.dumps(rows,indent=2))
print('WEST SURVEY',len(rows))
print([(r['name'],r['lo'],r['hi']) for r in rows if 'rail' in r['name'].lower() or 'guard' in r['name'].lower() or 'deck' in r['name'].lower()][:70])
