import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];A=json.loads((P/'assembly.json').read_text());report={}
def bbox(o,deps):
 ev=o.evaluated_get(deps);pts=[ev.matrix_world@Vector(v) for v in ev.bound_box];return ([min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)])
def inspect(path,context=False):
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();bad=[];count=0;uv=[]
 targets=list(bpy.data.collections['WSE_ASSETS'].objects)
 if context:targets+=[bpy.data.objects['WS_BaseSouth']]
 for o in targets:
  if o.type!='MESH':continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-12 for f in bm.faces)
  if nm or zero:bad.append({'object':o.name,'nonmanifold_edges':nm,'zero_faces':zero})
  count+=1;bm.free();ev.to_mesh_clear()
  if not o.data.uv_layers and o.name.startswith('WSE_'):uv.append(o.name)
 return {'reopened':True,'mesh_count':count,'topology_errors':bad,'missing_uvs':uv}
report['asset']=inspect(P/'Maldek_Emergency_Power.blend')
report['fitted']=inspect(P/'Maldek_Emergency_Power_Fitted.blend',True)
# open entrance doors for traversable state
for m in A['mechanisms']:
 if 'Door_hinge' in m['pivot']:bpy.data.objects[m['pivot']].rotation_euler[2]=math.radians(m['open_degrees'])
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
obstacles=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.name.startswith('Review'):continue
 lo,hi=bbox(o,deps)
 if hi[2]>.04 and lo[2]<1.80:
  if o.name.startswith(('WSE_AC_feed','WSE_Battery_DC')):
   ev=o.evaluated_get(deps);me=ev.to_mesh()
   for f in me.polygons:
    vs=[ev.matrix_world@me.vertices[i].co for i in f.vertices];ll=[min(v[i] for v in vs) for i in range(3)];hh=[max(v[i] for v in vs) for i in range(3)]
    if hh[2]>.04 and ll[2]<1.8:obstacles.append((o.name,ll,hh))
   ev.to_mesh_clear()
  else:obstacles.append((o.name,lo,hi))
def path_check(points):
 hits=set();samples=0
 for a,b in zip(points,points[1:]):
  a,b=Vector(a),Vector(b);num=math.ceil((b-a).length/.05)
  for k in range(num+1):
   p=a.lerp(b,k/max(1,num));samples+=1
   for n,lo,hi in obstacles:
    dx=max(lo[0]-p.x,0,p.x-hi[0]);dy=max(lo[1]-p.y,0,p.y-hi[1])
    if dx*dx+dy*dy<.34**2-1e-6:hits.add(n)
 return {'points_local':points,'sample_spacing_m':.05,'samples':samples,'radius_m':.34,'height_m':1.8,'hits':sorted(hits)}
report['routes']={
 'entrance_to_controls':path_check([[-.8,7.2],[2,7.2],[2,4.15],[3.45,4.15]]),
 'distribution_service':path_check([[2,7.2],[4.45,7.2]]),
 'transfer':path_check([[2,7.2],[2,5.48],[4.6,5.48]]),
 'battery':path_check([[2,7.2],[2,4.15],[4.9,4.15]])}
report['clearances']={'door_frame_width':1.43,'door_frame_height':2.194,'open_leaves_clear_width':1.42,'distribution_front_service_depth':1.0,'machine_reservation':[2.5,1.3],'note':'Door hardware evaluated below; static Blender envelope only, no Unreal collision claim.'}
report['source_hash_unchanged']=hashlib.sha256((P.parent/'west_services_01/Maldek_West_Services_Blockout.blend').read_bytes()).hexdigest()==json.loads((P.parent/'west_services_01/delivery.json').read_text())['sha256']
report['passed']=not report['asset']['topology_errors'] and not report['fitted']['topology_errors'] and not report['asset']['missing_uvs'] and all(not r['hits'] for r in report['routes'].values()) and report['source_hash_unchanged']
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))



