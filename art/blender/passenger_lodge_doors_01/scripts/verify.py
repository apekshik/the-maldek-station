"""Reopen evaluated geometry; exact mesh surface swing tests + conservative route proxies."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'))
s=bpy.data.scenes['PLD_Fitted_Doors'];bpy.context.window.scene=s
manifest=json.loads((OUT/'replacement_manifest.json').read_text())
report={'saved_reopened':True,'failures':[],'topology':[],'swing':[],'opening_rays':[],'route_clearance':[]}
def evaluated(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
 v=[o.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons]
 e.to_mesh_clear();return v,f
def tree(o):
 v,f=evaluated(o);return BVHTree.FromPolygons(v,f,all_triangles=False),v
def descendant(o,p):
 while o.parent:
  if o.parent==p:return True
  o=o.parent
 return False
def bounds(v):return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])
def overlap(a,b):return all(a[0][i]<b[1][i]-1e-5 and a[1][i]>b[0][i]+1e-5 for i in range(3))
for o in bpy.data.collections['PLD_ASSETS'].all_objects:
 if o.type!='MESH':continue
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 bad=sum(not x.is_manifold for x in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces)
 if bad or deg:report['failures'].append({'topology':o.name,'nonmanifold_edges':bad,'degenerate_faces':deg})
 report['topology'].append({'name':o.name,'nonmanifold_edges':bad,'degenerate_faces':deg});bm.free();e.to_mesh_clear()
 assert all(abs(v-1)<1e-6 for v in o.scale),o.name
print('TOPOLOGY',len(report['topology']),len(report['failures']),flush=True)
# Convex hull / segment distance in plan; route body radius .34 m (source layout proxy).
def hull(points):
 p=sorted(set((float(v.x),float(v.y)) for v in points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lo=[];hi=[]
 for q in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>1 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
def distance(p,poly):
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 if all(cross(poly[i],poly[(i+1)%len(poly)],p)>=0 for i in range(len(poly))):return 0.
 result=1e9
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
  result=min(result,math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))
 return result
routes={
 'ARRIVAL':{'coffee_queue':[[-17.1,-5.7],[-21.1,-5.7]],'court_remote_route':[[-17.1,-13],[-17.1,-9]],'door_traversal':[[-17.1,-9],[-17.1,-5.4]]},
 'GONDOLA':{'grating_promenade':[[-22,5.5],[-12,5.5]],'door_traversal':[[-17.1,2],[-17.1,5.5]]},
 'STAFF':{'main_arrival_route':[[-17.1,-12.8],[-17.1,-8.5]],'staff_traversal':[[-21.5,-10.5],[-18.1,-10.5]]}}
for d in manifest['doors']:
 P='PLD_'+d['id']+'_';pivot=bpy.data.objects[P+'LEAF_PIVOT'];T=Matrix(d['matrix_world']);W=d['width'];H=d['height']
 moving=[o for o in bpy.data.collections[P+'Assembly'].objects if o.type=='MESH' and descendant(o,pivot)]
 s.frame_set(1);bpy.context.view_layer.update()
 # Coplanar head/jamb cover corners must butt, never overlap in height.
 for ob in bpy.data.collections[P+'Assembly'].objects:
  if 'Jamb_Cover' in ob.name:
   points=[T.inverted()@v for v in evaluated(ob)[0]]
   if max(v.z for v in points)>H+.00001:report['failures'].append({'cover_joint_overlap':ob.name})
 seal=bpy.data.objects[P+'BOTTOM_SEAL'];sv,_=evaluated(seal);sv=[T.inverted()@v for v in sv]
 if abs(min(v.z for v in sv))>.001 or max(v.z for v in sv)<.023:report['failures'].append({'bottom_seal_bridge':d['id']})
 slabtree,_=tree(bpy.data.objects[P+'Leaf_Steel']);glasstree,_=tree(bpy.data.objects[P+'Glass'])
 ray=T@Vector((W/2,-.5,(1.34+H-.14)/2));direction=T.to_3x3()@Vector((0,1,0))
 if slabtree.ray_cast(ray,direction,1.)[0] is not None or glasstree.ray_cast(ray,direction,1.)[0] is None:report['failures'].append({'vision_aperture':d['id']})
 pivot.animation_data_clear()
 # Latch and bottom seal retracted for movement; explicit rotation independent of animation interpolation.
 s.frame_set(80);pivot.rotation_euler.z=0;bpy.context.view_layer.update()
 static=[]
 near=[min(d['origin'][i]-2.0,d['origin'][i]+2.0) for i in range(3)],[d['origin'][i]+2.5 for i in range(3)]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render or o in moving:continue
  if any(c.name=='PLD_REFERENCE_ONLY_Removable_Roof' for c in o.users_collection):continue
  if o.name.startswith(P) and not any(k in o.name for k in ['PATCH','Reveal','Cover','Drip']):continue
  vs=[o.matrix_world@Vector(p) for p in o.bound_box]
  if not overlap(bounds(vs),near):continue
  tr,v=tree(o);static.append((o.name,tr,bounds(v)))
 bad=[];minroutes={n:1e9 for n in routes[d['id']]};fullroutes={}
 for angle in range(0,101,5):
  pivot.rotation_euler.z=math.radians(d['side']*angle);bpy.context.view_layer.update()
  allv=[]
  for o in moving:
   tr,v=tree(o);bb=bounds(v);allv.extend(v)
   for name,st,sb in static:
    if overlap(bb,sb) and tr.overlap(st):bad.append({'angle':angle,'moving':o.name,'fixed':name})
  poly=hull(allv)
  for name,pts in routes[d['id']].items():
   ds=[]
   for a,b in zip(pts,pts[1:]):
    N=math.ceil(math.dist(a,b)/.025)
    for i in range(N+1):ds.append(distance((a[0]+(b[0]-a[0])*i/N,a[1]+(b[1]-a[1])*i/N),poly)-.34)
   minroutes[name]=min(minroutes[name],min(ds))
   if angle==100:fullroutes[name]=min(ds)
  if angle in [0,45,100]:print(d['id'],angle,'contacts',len(bad),flush=True)
 report['swing'].append(dict(door=d['id'],sample_step_degrees=5,sampled_angles=21,stationary_candidates=len(static),surface_collisions=bad))
 if bad:report['failures'].append({'swing':d['id'],'collision_count':len(bad)})
 for name in minroutes:
  traversal='traversal' in name
  check=fullroutes[name] if traversal else minroutes[name]
  report['route_clearance'].append(dict(door=d['id'],route=name,radius_m=.34,min_sweep_margin_m=minroutes[name],fully_open_margin_m=fullroutes[name],required='fully open only; doorway is occupied during movement' if traversal else 'all sampled swing angles'))
  if check<-.001:report['failures'].append({'route':name,'door':d['id'],'margin_m':check})
 # Exact clear aperture rays, 2 mm inside the specified nominal limits, through all layers.
 fixed=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render:continue
  vs=[o.matrix_world@Vector(p) for p in o.bound_box]
  if overlap(bounds(vs),near):fixed.append((o.name,tree(o)[0]))
 blocked=[];rays=0
 for u in [.002,W*.25,W*.5,W*.75,W-.002]:
  for z in [.020,.5,1.0,1.7,H-.002]:
   origin=T@Vector((u,-.5,z));direction=T.to_3x3()@Vector((0,1,0));rays+=1
   for name,tr in fixed:
    hit=tr.ray_cast(origin,direction,1.)
    if hit[0] is not None:blocked.append(dict(u=u,z=z,object=name))
 report['opening_rays'].append(dict(door=d['id'],width=W,height=H,rays=rays,blocked=blocked))
 if blocked:report['failures'].append({'opening':d['id'],'blocked':blocked})
print('GEOMETRY_DONE',flush=True)
report['source_unchanged']=hashlib.sha256((OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend').read_bytes()).hexdigest()==manifest['source_sha256']
retained=json.loads((OUT/'reference_transforms.json').read_text());replaced={p['source_object']:p['replacement_object'] for p in json.loads((OUT/'wall_patches.json').read_text())['patches']}
report['reference_transform_checks']=len(retained)
for rec in retained:
 ob=s.objects.get(replaced.get(rec['name'],rec['name']))
 if ob is None:report['failures'].append({'missing_context':rec['name']});continue
 delta=max(abs(ob.matrix_world[i][j]-rec['matrix_world'][i][j]) for i in range(4) for j in range(4))
 if delta>1e-5:report['failures'].append({'moved_context':rec['name'],'matrix_delta':delta})
report['passed']=not report['failures'] and report['source_unchanged']
report['limits']='Blender evaluated manifold and mesh-surface checks at 5-degree intervals plus 0.34 m radius plan-route samples. Not a continuous collision proof, structural certification, engine collision, or PIE test. Door traversal is tested fully open; during movement the doorway must be kept clear.'
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print('VERIFIED',report['passed'],report['failures'][:10],flush=True)
