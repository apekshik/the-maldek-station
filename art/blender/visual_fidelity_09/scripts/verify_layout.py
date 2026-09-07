import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Service_Apron_Refinement.blend'))
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];objects=[]
for c in bpy.data.collections:
 if not c.name.startswith(('VF08_','VF09_','VF06_Water_Tower')) or c.name.endswith('Presentation'):continue
 for o in c.objects:
  if o.type not in ['MESH','CURVE','FONT'] or o.hide_render:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();offset=len(verts);verts.extend([o.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(offset+i for i in p.vertices) for p in me.polygons]);objects.append(o.name);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
routes={'entry':[(25.9,-15),(29,-15)],'left_service':[(29,-17.2),(29,-10.2)],'right_service':[(34.6,-17.2),(34.6,-10.2)],'rear_cross_aisle':[(29,-17.2),(35.1,-17.2)],'workshop':[(34.6,-15.5),(39,-15.5)],'fuel_exit':[(29.5,-17.2),(29.5,-19.6),(26.1,-19.6)]}
routes['emergency_fill_access']=[(26.2,-19.3),(26.2,-20.1),(25.2,-20.5),(25.2,-23.15),(25.9,-23.15)]
routes['water_pad_connection']=[(25.2,-18.2),(23.55,-18.2)]
routes['water_north_border']=[(23.55,-18.2),(23.55,-15.5),(18.3,-15.5)]
routes['water_south_border']=[(23.55,-18.2),(23.55,-20.7),(18.3,-20.7)]
routes['incoming_service_ramp']=[tuple(p) for p in json.loads((OUT/'layout.json').read_text())['approach_centerline']]+[(25.2,-13.8,-1)]
results=[]
for name,points in routes.items():
 points=[(*p,-1) if len(p)==2 else p for p in points]
 failures=[];count=0
 for a,b in zip(points,points[1:]):
  n=math.ceil(math.dist(a,b)/.20);dx=(b[0]-a[0]);dy=(b[1]-a[1]);ln=math.hypot(dx,dy);perp=Vector((-dy/ln,dx/ln,0))
  for j in range(n+1):
   p=Vector((a[0]+dx*j/n,a[1]+dy*j/n,a[2]+(b[2]-a[2])*j/n));count+=1
   for side in [-.28,0,.28]:
    q=p+perp*side;hit=bvh.ray_cast(q+Vector((0,0,.3)),Vector((0,0,-1)),.65)
    if hit[0] is None or abs(hit[0].z-q.z)>.06:
     supported=False
     for ox,oy in [(v,0) for v in [-.07+i*.005 for i in range(29)]]+[(0,v) for v in [-.07+i*.005 for i in range(29)]]:
      h=bvh.ray_cast(q+Vector((ox,oy,.3)),Vector((0,0,-1)),.65)
      if h[0] is not None and abs(h[0].z-q.z)<.06:supported=True;break
     if not supported:failures.append({'p':list(q),'reason':'floor_patch'})
   for z in [.2,.9,1.65,2.05]:
    q=p+Vector((0,0,z))
    for direction in [Vector((1,0,0)),Vector((-1,0,0)),Vector((0,1,0)),Vector((0,-1,0)),Vector((0,0,1))]:
     if bvh.ray_cast(q,direction,.28)[0] is not None:failures.append({'p':list(q),'reason':'body_clearance'});break
 results.append({'route':name,'samples':count,'passed':not failures,'failures':failures[:15]})
report=json.loads((OUT/'layout.json').read_text());anchors=[]
for name,old in report['preserved_bounds'].items():
 o=bpy.data.objects[name];pts=[o.matrix_world@Vector(v) for v in o.bound_box];new=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]];anchors.append({'name':name,'passed':max(abs(new[i][j]-old[i][j]) for i in range(2) for j in range(3))<.00001})
r={'evaluated_objects':len(objects),'vertices':len(verts),'polygons':len(faces),'routes':results,'anchors':anchors,'scope':'Blender sampled floor patches (70 mm search on grating), 560 mm body clearance; not Unreal capsule verification','passed':all(x['passed'] for x in results+anchors)}
(OUT/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
