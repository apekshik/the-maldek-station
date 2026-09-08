import bpy,json
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[4]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(repo/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'),link=False) as (a,b):b.collections=['12_Gondola','VF06_Gondola_Details']
for c in b.collections:bpy.context.scene.collection.children.link(c)
bpy.context.view_layer.update();rows=[]
for o in bpy.context.scene.objects:
 if o.type not in {'MESH','FONT','CURVE'}:continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 rows.append({'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'lo':[min(p[i] for p in pts) for i in range(3)],'hi':[max(p[i] for p in pts) for i in range(3)],'materials':[m.name for m in o.data.materials],'text':o.data.body if o.type=='FONT' else None})
(repo/'art/blender/gondola_cabin_01/audit.json').write_text(json.dumps(rows,indent=2))
