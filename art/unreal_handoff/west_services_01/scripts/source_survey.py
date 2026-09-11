import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];src=P.parents[1]/'blender/station_dressing_01/Maldek_Station_Furnished.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if not o.name.startswith(('WS_','WS02_','WSP_','WSR_','WSE_','SD_')):continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'matrix':[list(r) for r in o.matrix_world],'lo':[min(v[j] for v in bb) for j in range(3)],'hi':[max(v[j] for v in bb) for j in range(3)],'materials':[m.name for m in o.data.materials if m] if hasattr(o.data,'materials') else []})
mats={}
for m in bpy.data.materials:
 if m.name in {n for r in rows for n in r['materials']}:mats[m.name]={'nodes':[n.type for n in m.node_tree.nodes] if m.use_nodes else [],'color':list(m.diffuse_color)}
(P/'source_inventory.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'objects':rows,'materials':mats},indent=2));print('SURVEY',len(rows),len(mats))
