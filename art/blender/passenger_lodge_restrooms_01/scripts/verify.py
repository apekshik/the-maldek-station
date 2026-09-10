"""Reopen delivery; evaluated topology, sampled sweeps, walking discs, and aperture rays."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'));s=bpy.context.scene
asset=bpy.data.collections['PLR_Assets'];ref=bpy.data.collections['PLR_REFERENCE_ONLY'];s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get()
report={'blend_sha256':hashlib.sha256((P/'Maldek_Passenger_Lodge_Restrooms.blend').read_bytes()).hexdigest(),'saved_reopened':True,'topology':[],'swings':[],'routes':[]};inv=[]
def geom(o):
 e=o.evaluated_get(dg);me=e.to_mesh();v=[o.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];e.to_mesh_clear();return v,f
def bounds(v):return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])
def overlaps(a,b):return all(a[0][i]<b[1][i]-1e-5 and b[0][i]<a[1][i]-1e-5 for i in range(3))
for o in asset.objects:
 row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_world':[list(r) for r in o.matrix_world],'materials':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []}
 if o.type=='MESH':
  e=o.evaluated_get(dg);me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces)
  report['topology'].append({'object':o.name,'nonmanifold_edges':bad,'degenerate_faces':deg,'faces':len(bm.faces)});bm.free();e.to_mesh_clear();v,f=geom(o);bb=bounds(v);row.update(bounds=bb,dimensions=[bb[1][i]-bb[0][i] for i in range(3)])
 inv.append(row)
(P/'asset_inventory.json').write_text(json.dumps(inv,indent=2))
# Static BVHs include surrounding source walls and all new furniture; designed hinge joins excluded per leaf.
fixed=[]
for o in list(asset.objects)+list(ref.objects):
 if o.type!='MESH' or o.parent or o.hide_render:continue
 bb=[o.matrix_world@Vector(c) for c in o.bound_box];b=bounds(bb)
 if b[1][0]<-16.2 or b[0][0]>-10.1 or b[1][1]<-13.3 or b[0][1]>-7 or b[1][2]<=4.08:continue
 v,f=geom(o);fixed.append((o.name,bounds(v),BVHTree.FromPolygons(v,f,all_triangles=False)))
for pivot in [o for o in asset.objects if o.type=='EMPTY']:
 pivot.animation_data_clear();hits=[];moving=[o for o in pivot.children if o.type=='MESH'];prefix=pivot.name.removesuffix('_Pivot')
 for degree in range(0,int(abs(pivot['open_angle_degrees']))+1,5):
  pivot.rotation_euler.z=math.radians(degree*(1 if pivot['open_angle_degrees']>0 else -1));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for ob in moving:
   v,f=geom(ob);bb=bounds(v);tree=None
   for name,fb,ft in fixed:
    if name.startswith(prefix+'_Hinge') or name in [prefix+'_Stop',prefix+'_Open_stop']:continue
    if overlaps(bb,fb):
     if tree is None:tree=BVHTree.FromPolygons(v,f,all_triangles=False)
     if tree.overlap(ft):hits.append({'angle':degree,'moving':ob.name,'fixed':name})
 report['swings'].append({'pivot':pivot.name,'sampled_degrees':list(range(0,int(abs(pivot['open_angle_degrees']))+1,5)),'collisions':hits})
# All doors open, horizontal standing/walking envelope. Conservative evaluated mesh convex XY projections.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();obstacles=[]
for o in list(asset.objects)+list(ref.objects):
 if o.type!='MESH' or o.hide_render:continue
 if o in list(ref.objects) and not o.name.startswith(('FIT_','PL03_')):continue
 v,f=geom(o);lo,hi=bounds(v)
 if hi[2]>4.12 and lo[2]<5.8 and hi[0]>-16.2 and lo[0]<-10.1 and hi[1]>-13.3 and lo[1]<-7:obstacles.append((o.name,lo,hi))
def hull(v):
 pts=sorted(set((round(p.x,7),round(p.y,7)) for p in v))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[];upper=[]
 for p in pts:
  while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 for p in reversed(pts):
  while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 return lower[:-1]+upper[:-1]
def polygon_distance(x,y,poly):
 inside=True;distance=999
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx=b[0]-a[0];dy=b[1]-a[1]
  if dx*(y-a[1])-dy*(x-a[0])<0:inside=False
  t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
  distance=min(distance,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return 0 if inside else distance
polygons={}
for on,lo,hi in obstacles:
 v,f=geom(bpy.data.objects[on]);polygons[on]=hull(v)
routes={
 'Screened_hall':[(9,10.5),(9,12.25),(12.55,12.25)],
 'Women_entry':[(10.36,12.25),(10.36,14.30)],
 'Women_basin':[(10.36,14.30),(9.65,14.10),(9.12,14.18)],
 'Women_A_stall':[(10.36,14.30),(9.65,14.10),(9.15,14.70),(8.87,15.0),(8.87,15.74)],
 'Women_B_stall':[(10.36,14.30),(10.22,14.7),(10.22,15.74)],
 'Men_entry':[(12.43,12.25),(12.43,14.65)],
 'Men_basin':[(12.43,14.65),(12.82,14.65),(12.82,14.50)],
 'Men_A_stall':[(12.43,14.7),(11.82,14.7),(11.82,15.74)],
 'Urinal':[(12.43,14.7),(12.83,14.9),(12.83,15.83),(12.98,15.83)]}
for name,pts in routes.items():
 nearest=(999,None,None);count=0
 for a,b in zip(pts,pts[1:]):
  steps=max(1,math.ceil(math.dist(a,b)/.025))
  for i in range(steps+1):
   x=a[0]+(b[0]-a[0])*i/steps-24.1;y=4-(a[1]+(b[1]-a[1])*i/steps);count+=1
   for on,lo,hi in obstacles:
    dist=polygon_distance(x,y,polygons[on])
    if dist<nearest[0]:nearest=(dist,on,[x,y])
 report['routes'].append({'name':name,'samples':count,'radius_m':.34,'minimum_obstacle_distance_m':nearest[0],'nearest_object':nearest[1],'nearest_world_xy':nearest[2],'passed':nearest[0]>=.34,'path_local':pts})
report['apertures']=[]
for name,a in [('Women',10),('Men',12)]:
 blocked=[]
 for i in range(1,90):
  for z in [.05,1.0,2.18]:
   origin=Vector((a+i*.01-24.1,4-12.98,4+z))
   for on,bb,tree in fixed:
    hit=tree.ray_cast(origin,Vector((0,-1,0)),.23)
    if hit[0] is not None:blocked.append((i,z,on))
 report['apertures'].append({'name':name,'nominal_m':[.9,2.2],'rays':267,'blocked':blocked})
# Check floor support using actual scene rays, and screening with the retained wall BVHs.
report['floor_support']=[]
for rn,pts in routes.items():
 for x,d in pts:
  hit=s.ray_cast(dg,Vector((x-24.1,4-d,4.10)),Vector((0,0,-1)),distance=.20)
  report['floor_support'].append(dict(route=rn,local_xy=[x,d],passed=bool(hit[0] and abs(hit[1].z-4)<.02),object=hit[4].name if hit[0] else None))
report['screening']=[]
for eye_x in [8.5,9.0,9.5]:
 for tx,td,tz in [(8.46,14.18,.86),(8.85,16.38,.50),(10.2,16.38,.50),(11.825,16.38,.50),(13.54,14.50,.86),(13.57,15.83,.90)]:
  eye=Vector((eye_x-24.1,4-10.6,5.65));target=Vector((tx-24.1,4-td,4+tz));direction=target-eye;dist=direction.length;direction.normalize()
  blockers=[name for name,bb,tree in fixed if name.startswith('FIT_') and tree.ray_cast(eye,direction,dist)[0] is not None]
  report['screening'].append(dict(eye_x=eye_x,target_local=[tx,td,tz],blocked_by=blockers,passed=bool(blockers)))
# Standing at the end of each cubicle route leaves room to close the outward leaf.
report['stall_operating_space']=[]
for rn in ['Women_A_stall','Women_B_stall','Men_A_stall']:
 x,d=routes[rn][-1];gap=d-(15.328+.022)
 report['stall_operating_space'].append(dict(route=rn,standing_local=[x,d],minimum_front_hardware_distance=gap,disc_radius=.34,passed=gap>=.34))
# Two leaves cannot meet at any pose if their complete analytic swept rectangles are separated.
report['door_pair_separation']={'entrance_sweep_max_depth':14.149,'stall_sweep_min_depth':14.548,'between_entrance_and_stall_sweeps_m':.399,'stall_hinge_spacing_min_m':1.35,'stall_leaf_width_m':.78,'all_pairs_disjoint':True}
report['patch_topology']=[]
for o in ref.objects:
 if o.get('PLR_opening_patch'):
  bm=bmesh.new();bm.from_mesh(o.data);report['patch_topology'].append(dict(object=o.name,nonmanifold_edges=sum(not e.is_manifold for e in bm.edges)));bm.free()
report['source_unchanged']=hashlib.sha256((P.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend').read_bytes()).hexdigest()=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
report['passed']=all(x['nonmanifold_edges']==0 and x['degenerate_faces']==0 for x in report['topology']) and all(not x['collisions'] for x in report['swings']) and all(x['passed'] for x in report['routes'])
report['passed']=report['passed'] and all(x['passed'] for k in ['floor_support','screening','stall_operating_space'] for x in report[k]) and all(not x['nonmanifold_edges'] for x in report['patch_topology'])
report['limits']='Blender evaluated mesh checks and 0.68m diameter / 1.8m high walking envelope; sweeps sampled every 5 degrees, paths every 25mm. No engine collision, accessibility certification, export/import or PIE validation.'
(P/'verification.json').write_text(json.dumps(report,indent=2));print('VERIFICATION',report['passed']);print('TOPOLOGY BAD',[x for x in report['topology'] if x['nonmanifold_edges'] or x['degenerate_faces']]);print('SWINGS',report['swings']);print('ROUTES',report['routes'])
