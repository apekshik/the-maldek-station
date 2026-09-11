import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P.parent/'west_services_02/Maldek_Station_West_Integrated.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in ps) for i in range(3)];hi=[max(v[i] for v in ps) for i in range(3)]
 if 'clean' in o.name.lower() or (o.name.startswith(('WSR_','WSE_')) and any(k in o.name.lower() for k in ['shelf','cupboard','cabinet','cot','heater','radio','door','case'])):rows.append({'name':o.name,'lo':lo,'hi':hi})
(P/'survey.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
