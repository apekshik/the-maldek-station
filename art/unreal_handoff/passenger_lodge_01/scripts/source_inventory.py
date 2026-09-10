import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.context.scene;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 rows.append({'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection], 'hidden':o.hide_render,'visible':o.visible_get(),'lo':[min(p[i] for p in ps) for i in range(3)],'hi':[max(p[i] for p in ps) for i in range(3)],'materials':[m.name if m else None for m in o.data.materials]})
(OUT/'source_inventory.json').write_text(json.dumps(rows,indent=2))
print('SOURCE_INVENTORY',len(rows))
