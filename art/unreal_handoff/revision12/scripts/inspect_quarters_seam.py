"""Read-only source geometry evidence for the interior floor line."""
import bpy,json
from mathutils import Vector
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(repo/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'))
rows=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in bpy.data.objects:
 if ob.type!='MESH' or not any(c.name in ['VF06_Quarters','VF06_Control'] for c in ob.users_collection):continue
 ev=ob.evaluated_get(dg);pts=[ev.matrix_world@Vector(p) for p in ev.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if lo[2]<7.7 and hi[2]>7.59 and hi[0]>-7.5 and lo[0]<-1.6 and hi[1]>-4.4 and lo[1]<1.1:
  rows.append({'name':ob.name,'min':lo,'max':hi})
(b/'quarters_floor_source_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
