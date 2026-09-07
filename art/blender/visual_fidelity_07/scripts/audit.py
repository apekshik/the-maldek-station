import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'visual_fidelity_06/Maldek_Integrated_Station.blend'))
bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 rows.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],bounds=[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],hide=o.hide_render))
(OUT/'source_objects.json').write_text(json.dumps(rows,indent=2))
