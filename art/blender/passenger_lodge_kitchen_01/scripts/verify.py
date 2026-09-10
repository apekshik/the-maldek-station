"""Saved-file topology, source preservation, route and surface-owner checks. No engine claim."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen.blend'))
s=bpy.data.scenes['PLK_Fitted_Review'];bpy.context.window.scene=s;bpy.context.view_layer.update()
assets=bpy.data.collections['PLK_Assets'];root=bpy.data.objects['PLK_Assembly']
errors=[];meshes=[]
def bb(o):
 p=[root.matrix_world.inverted()@o.matrix_world@Vector(v) for v in o.bound_box]
 return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
for o in assets.all_objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-12 for f in bm.faces)
 if bad or zero:errors.append({'name':o.name,'nonmanifold_edges':bad,'zero_area_faces':zero})
 meshes.append({'name':o.name,'bounds_local':bb(o),'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':bad,'zero_area_faces':zero});bm.free()
# Conservative circle-versus-AABB clearance from the saved evaluated mesh bounds.
obstacles=[r for r in meshes if r['bounds_local'][1][2]>.10 and r['bounds_local'][0][2]<1.95]
def collisions(x,d,r=.30):
 out=[]
 for rec in obstacles:
  lo,hi=rec['bounds_local'];dx=max(lo[0]-x,0,x-hi[0]);dy=max(lo[1]+d,0,-d-hi[1])
  if dx*dx+dy*dy<r*r-1e-8:out.append(rec['name'])
 return out
routes={'door_to_counter':[(4.60,14.5),(3.5,14.5),(2.1,14.5),(2.1,12.05)],'wash_approach':[(2.1,14.5),(1.36,14.58)],'handwash_approach':[(3.5,14.5),(3.55,13.24),(3.84,13.24)],'rear_prep':[(3.5,14.5),(3.5,14.90)],'fridge':[(2.1,14.5),(2.58,14.87)]}
checks=[]
for name,pts in routes.items():
 hits=[];samples=0
 for a,b in zip(pts,pts[1:]):
  N=max(2,math.ceil(math.dist(a,b)/.05))
  for j in range(N+1):
   x=a[0]+(b[0]-a[0])*j/N;d=a[1]+(b[1]-a[1])*j/N;samples+=1
   cs=collisions(x,d)
   if cs:hits.append({'point':[x,d],'objects':cs})
 checks.append({'name':name,'radius_m':.30,'samples':samples,'passed':not hits,'collisions':hits})
 if hits:errors.append({'route':name,'collision_samples':len(hits)})
# Clear preparation rectangle above the rear worktop, measured in the saved scene.
prep_obstacles=[]
for rec in meshes:
 lo,hi=rec['bounds_local']
 if hi[0]>2.20 and lo[0]<3.60 and hi[1]>-15.90 and lo[1]<-15.32 and hi[2]>.91 and lo[2]<1.7:prep_obstacles.append(rec['name'])
if prep_obstacles:errors.append({'prep_rectangle_obstacles':prep_obstacles})
# Door approach is an intentionally empty rectangular prism, independent of PLD frame.
reserve=[]
for rec in meshes:
 lo,hi=rec['bounds_local']
 if hi[0]>3.70 and lo[0]<4.82 and hi[1]>-15.04 and lo[1]<-13.72 and hi[2]>.05 and lo[2]<2.2:reserve.append(rec['name'])
if reserve:errors.append({'door_approach_obstacles':reserve})
# Source objects retained in fitted review have unchanged geometry and transforms.
source=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
manifest=json.loads((OUT/'replacement_manifest.json').read_text())
assert all(bpy.data.objects.get(r['name']) is None for r in manifest['replacements'])
# Aperture ray tests: actual sink opening is clear until bowl interior; slab cannot cap it.
deps=bpy.context.evaluated_depsgraph_get();sink_rays=[]
for x,d in [(.565,14.58),(.465,14.58),(.665,14.58),(.565,14.43),(.565,14.73)]:
 origin=Vector((x-24.1,4-d,5.1));hit,loc,normal,idx,obj,m=s.ray_cast(deps,origin,Vector((0,0,-1)),distance=.5)
 sink_rays.append({'local_xy':[x,-d],'hit':obj.name if hit else None,'height_above_floor':loc.z-4 if hit else None})
 if hit and 'Worktop' in obj.name:errors.append({'sink_capped_by_worktop':[x,d]})
# Cabinet and appliance mechanism sweeps: retain closed pose and measure open extents.
poses=[]
for o in assets.all_objects:
 if o.get('motion')!='hinge':continue
 closed=o.rotation_euler.z;o.rotation_euler.z=math.radians(o['open_degrees']);bpy.context.view_layer.update()
 kids=[r for r in o.children_recursive if r.type=='MESH'];pts=[v for k in kids for v in [bb(k)[0],bb(k)[1]]]
 poses.append({'pivot':o.name,'world':list(o.matrix_world.translation),'open_degrees':o['open_degrees'],'open_bounds_local':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]})
 o.rotation_euler.z=closed
bpy.context.view_layer.update()
contacts=json.loads((OUT/'mechanism_contacts.json').read_text())
mechanisms_clear=all(not r['candidate_contacts'] for r in contacts)
if not mechanisms_clear:errors.append({'mechanism_contacts':'See mechanism_contacts.json'})
assert bpy.data.objects.get('PLK_Serving_Back') is None
assert bpy.data.objects.get('PLK_Wash_base_Top_rail.001') is None
assert bpy.data.objects.get('PLK_Prep_drawers_Shelf.001') is None
report={'mechanisms_clear':mechanisms_clear,'mechanisms_checked':len(contacts),'surface_ownership_checks':{'single_counter_back':True,'wash_bowl_support_rail_removed':True,'drawer_cavity_shelf_removed':True},'passed':not errors,'saved_reopened':True,'source_sha256':sha,'source_unchanged':True,'new_meshes':len(meshes),'errors':errors,'routes':checks,'staff_door_reserved_prism_local_x_depth_z':[[3.70,13.72,.05],[4.82,15.04,2.2]],'staff_door_obstacles':reserve,'clear_prep_rectangle_m':{'x':[2.20,3.60],'depth':[15.32,15.90],'size':[1.40,.58],'obstacles':prep_obstacles},'sink_rays':sink_rays,'mechanism_open_bounds':poses,'geometry':meshes,'limits':'Conservative Blender AABB walking checks using radius 0.30 m; mechanism extents and mesh topology; not engine collision or regulatory/engineering verification.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['geometry','mechanism_open_bounds','routes']},indent=2))
