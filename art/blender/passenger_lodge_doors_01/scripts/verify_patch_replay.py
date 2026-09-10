"""Compare regenerated opening patches with the delivered source-fitted patches."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
mapping={p['source_object']:p['replacement_object'] for p in json.loads((OUT/'wall_patches.json').read_text())['patches']}
def evaluated(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 v=[o.matrix_world@x.co for x in m.vertices];f=[list(x.vertices) for x in m.polygons]
 e.to_mesh_clear();return v,BVHTree.FromPolygons(v,f)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'));bpy.context.window.scene=bpy.data.scenes['PLD_Fitted_Doors']
expected={n:evaluated(bpy.data.objects[r]) for n,r in mapping.items()}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Opening_Patch_Review.blend'));bpy.context.window.scene=bpy.data.scenes['05_Material_Study']
results=[]
for name,(av,at) in expected.items():
 bv,bt=evaluated(bpy.data.objects[name]);distances=[bt.find_nearest(v)[3] for v in av]+[at.find_nearest(v)[3] for v in bv]
 delta=max(distances);results.append(dict(source_object=name,max_symmetric_vertex_surface_distance_m=delta,passed=delta<.00005))
report=dict(passed=all(r['passed'] for r in results),objects=results,tolerance_m=.00005,method='Every evaluated vertex compared to the opposite evaluated surface, in both directions after reopening both files.')
(OUT/'patch_replay_verification.json').write_text(json.dumps(report,indent=2));print(report)
assert report['passed']
