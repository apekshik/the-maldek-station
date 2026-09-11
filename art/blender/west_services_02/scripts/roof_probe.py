import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Station_West_Integrated.blend'));s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def geom(o):
 e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@x.co for x in m.vertices];f=[list(p.vertices) for p in m.polygons];e.to_mesh_clear();return BVHTree.FromPolygons(v,f),[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
roof=[o for o in bpy.data.collections['WS_SHARED_ROOF'].all_objects if o.type=='MESH'];power=[o for o in bpy.data.collections['WSE_ASSETS'].all_objects if o.type=='MESH'];hits=[]
for ob in power:
 ps=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 if max(v.z for v in ps)<7:continue
 t,b=geom(ob);print('HIGH',ob.name,b)
 for r in roof:
  rt,rb=geom(r)
  if all(b[0][i]<rb[1][i] and b[1][i]>rb[0][i] for i in range(3)) and t.overlap(rt):hits.append([ob.name,r.name])
(OUT/'roof_interface_probe.json').write_text(json.dumps(hits,indent=2));print('HITS',hits)
