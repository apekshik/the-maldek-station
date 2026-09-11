import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];D=json.loads((P/'exports.json').read_text());bpy.ops.wm.open_mainfile(filepath=D['source']);s=bpy.context.scene;s.frame_set(1)
for n in D['integration_repairs']['shelf_objects']:bpy.data.objects[n].location.x+=1.25
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();report=[]
F=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
failed={r['name'].replace('MIG_WS_',''):r for r in json.loads((P/'mechanism_runtime.json').read_text())['results'] if not r['open'] or not r['closed']}
for r in D['assets']:
 if r['key'] not in failed:continue
 q=failed[r['key']];fraction=(q['fraction']+.012 if not q['open'] else 0);M=Matrix(r['matrix'])@Matrix.Rotation(math.radians(r['control']['angle'])*fraction,4,'Z')
 for ci,c in enumerate(r['control']['collisions']):
  v=[M@Vector([c['center'][j]+sg[j]*max(.0005,c['extent'][j]-.0005) for j in range(3)]) for sg in [(x,y,z) for z in [-1,1] for y in [-1,1] for x in [-1,1]]];a=[min(p[j] for p in v) for j in range(3)];b=[max(p[j] for p in v) for j in range(3)];tree=BVHTree.FromPolygons(v,F)
  for rr in D['assets']:
   if rr['control'] or rr.get('nonblocking'):continue
   for n in rr['sources']:
    ob=s.objects[n]
    if ob.type not in ['MESH','CURVE','FONT']:continue
    bb=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(p[j] for p in bb) for j in range(3)];hi=[max(p[j] for p in bb) for j in range(3)]
    if any(b[j]<lo[j] or a[j]>hi[j] for j in range(3)):continue
    eo=ob.evaluated_get(dg);me=eo.to_mesh();bt=BVHTree.FromPolygons([ob.matrix_world@x.co for x in me.vertices],[tuple(f.vertices) for f in me.polygons]);hits=tree.overlap(bt);eo.to_mesh_clear()
    if hits:report.append({'mechanism':r['key'],'piece':ci,'source':c['source'],'hit':n,'fraction':fraction,'bounds':[lo,hi]})
(P/'collision_probe.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

