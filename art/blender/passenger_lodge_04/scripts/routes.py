"""Combined saved-lodge walking clearance, with operational doors open."""
import bpy,json,math,ast
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];ART=OUT.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;s.frame_set(1)
closed={o.name:o.matrix_basis.copy() for o in bpy.data.collections['PLK_Assets'].all_objects}
s.frame_set(100)
for name,mat in closed.items():
 o=s.objects[name]
 if o.animation_data:o.animation_data_clear()
 o.matrix_basis=mat
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for node in ast.parse((ART/'passenger_lodge_restrooms_01/scripts/verify.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['geom','bounds','hull','polygon_distance']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'route_helpers','exec'))
obstacles=[]
asset_names={n for p in json.loads((OUT/'reconciliation.json').read_text())['packages'] for n in p['objects']}
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 if o.name not in asset_names and not o.name.startswith(('FIT_','PL03_','PLSH_')):continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo,hi=bounds(ps)
 if hi[2]<=4.12 or lo[2]>=5.8 or hi[0]<-29 or lo[0]>-9 or hi[1]<-15 or lo[1]>6:continue
 v,f=geom(o);poly=hull(v)
 if len(poly)>2:obstacles.append((o.name,lo,hi,poly))
routes={x['name']:x['path_local'] for x in json.loads((ART/'passenger_lodge_restrooms_01/verification.json').read_text())['routes']}
routes.update({'Main_hall':[(7,10.4),(7,0.5)],'Lockers':[(7,9.8),(11.7,9.8),(13.1,9.8)],'Coffee_public':[(7,9.7),(2.6,9.7),(2.6,9.9)],'Kitchen_work':[(4.6,14.5),(3.5,14.5),(2.1,14.5),(2.1,12.05)],'Kitchen_handwash':[(3.5,14.5),(3.55,13.24),(3.84,13.24)],'Kitchen_prep':[(3.5,14.5),(3.5,14.90)]})
report={'conditions':'Public/restroom/locker doors open; kitchen cabinets closed. Radius 0.34 m, height 1.8 m; conservative XY hulls. Blender checks only.','routes':[]}
for name,pts in routes.items():
 nearest=(999,None,None);count=0
 for a,b in zip(pts,pts[1:]):
  N=max(1,math.ceil(math.dist(a,b)/.025))
  for i in range(N+1):
   x=a[0]+(b[0]-a[0])*i/N-24.1;y=4-a[1]-(b[1]-a[1])*i/N;count+=1
   for on,lo,hi,poly in obstacles:
    if x<lo[0]-1 or x>hi[0]+1 or y<lo[1]-1 or y>hi[1]+1:continue
    d=polygon_distance(x,y,poly)
    if d<nearest[0]:nearest=(d,on,[x,y])
 report['routes'].append({'name':name,'minimum_clearance_m':nearest[0],'nearest':nearest[1],'xy':nearest[2],'samples':count,'passed':nearest[0]>=.34})
for node in ast.parse((ART/'passenger_lodge_shell_01/scripts/verify.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name=='foot':exec(compile(ast.Module(body=[node],type_ignores=[]),'support_helper','exec'))
platform_paths={'Entry':[[-23.1,-14.3,4],[-17.1,-14.3,4],[-17.1,-6.8,4]],'Platform':[[-17.1,-6.8,4],[-17.1,5.5,4],[-4,5.5,4]],'Bypass':[[-17.1,-14.3,4],[-9.1,-14.3,4],[-9.1,-6.6,4],[-3.5,-6.6,4]],'West':[[-28,-14,4],[-28,5.5,4]]}
report['support_failures']=[];report['support_samples']=0
for name,pts in platform_paths.items():
 for a,b in zip(pts,pts[1:]):
  N=max(1,math.ceil(math.dist(a,b)/.25))
  for i in range(N+1):
   p=Vector(a).lerp(Vector(b),i/N);report['support_samples']+=1
   if not foot(p):report['support_failures'].append([name,list(p)])
for i in range(24):
 p=(-7.2,-14.42+(i+.5)*.28,(i+1)*4/24);report['support_samples']+=1
 if not foot(p):report['support_failures'].append(['Bypass_stair',p])
report['passed']=all(x['passed'] for x in report['routes']) and not report['support_failures']
(OUT/'routes.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
