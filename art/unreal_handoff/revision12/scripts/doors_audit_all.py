import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/apek-anna/Developer/the-maldek-station');bpy.ops.wm.open_mainfile(filepath=str(root/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'),load_ui=False)
rows=[]
for o in bpy.data.objects:
 if o.name.startswith(('Door_return','Door_lintel','Flush_threshold')):
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());p=[e.matrix_world@Vector(v) for v in e.bound_box]
  rows.append({'name':o.name,'collections':[c.name for c in o.users_collection],'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]})
(root/'art/unreal_handoff/revision12/doors/all_openings.json').write_text(json.dumps(rows,indent=2))
for r in rows:
 if r['name'].startswith('Flush_threshold'):print(r)
