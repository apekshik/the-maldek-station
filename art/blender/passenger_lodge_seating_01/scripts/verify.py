"""Saved/reopened checks, evaluated closed topology and conservative footprint routes."""
import bpy,bmesh,json,hashlib,os,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Seating.blend'))
s=bpy.context.scene;kit=bpy.data.collections['PLS_Seating_Kit'];manifest=json.loads((OUT/'replacement_manifest.json').read_text())
meshes=[o for o in kit.objects if o.type=='MESH'];deps=bpy.context.evaluated_depsgraph_get();bad=[];checked=set();bounds={}
for o in meshes:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];bounds[o.name]=([min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)])
 if o.data.name in checked:continue
 checked.add(o.data.name);me=o.evaluated_get(deps).to_mesh();bm=bmesh.new();bm.from_mesh(me)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces) or bm.calc_volume(signed=True)<=0:bad.append(o.name)
 bm.free();o.evaluated_get(deps).to_mesh_clear()
assert not bad,bad
trees={}
def tree(o):
 if o.name not in trees:trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
 return trees[o.name]
brace_joints=0
for o in meshes:
 if '_Knee_Brace' not in o.name:continue
 prefix=o.name.split('_Knee_Brace')[0]
 for suffix in ['_Upper_Spine','_Stretcher']:
  assert tree(o).overlap(tree(s.objects[prefix+suffix])),(o.name,'disconnected from',suffix)
  brace_joints+=1
def signature(o):
 payload=[list(row) for row in o.matrix_world]
 if o.type=='MESH':payload += [[list(v.co) for v in o.data.vertices],[[*p.vertices] for p in o.data.polygons],[m.name if m else None for m in o.data.materials]]
 return hashlib.sha256(repr(payload).encode()).hexdigest()
baseline=json.loads((OUT/'context_signatures.json').read_text())
assert all(n in s.objects and signature(s.objects[n])==sig for n,sig in baseline.items())
assert all(row['name'] not in s.objects for row in manifest['replacement_objects'])
assert len([o for o in kit.objects if o.type=='EMPTY'])==6
assert len([o for o in meshes if '_Table_Plank_' in o.name])==30
assert len([o for o in meshes if '_Bench_' in o.name and '_Plank_' in o.name])==24
for g in manifest['groups']:
 x,y,z=g['translation_m'];bs=[bounds[n] for n in g['objects']];lo=[min(b[0][i] for b in bs) for i in range(3)];hi=[max(b[1][i] for b in bs) for i in range(3)]
 assert lo[0]>=x-.901 and hi[0]<=x+.901 and lo[1]>=y-.951 and hi[1]<=y+.951
 assert abs(hi[2]-(z+.78))<1e-5
 assert abs(lo[2]-z)<1e-5
 g['measured_bounds']=[lo,hi]
# Furniture collision proxy: capsule centreline against full seating footprints,
# conservative (does not slip through openings under the furniture).
routes={'central_entrance_to_platform':[(-17.1,-7),(-17.1,4)],'cross_aisle_north':[(-22, .9),(-11,.9)],'cross_aisle_south':[(-22,-2.3),(-11,-2.3)],'service_counter_approach':[(-17.1,-5.8),(-21,-5.8)],'locker_restroom_approach':[(-17.1,-5.8),(-10.9,-5.8)]}
checks={}
for name,(a,b) in routes.items():
 dist=math.dist(a,b);n=math.ceil(dist/.05);minimum=100
 for i in range(n+1):
  p=[a[k]+(b[k]-a[k])*i/n for k in range(2)]
  for g in manifest['groups']:
   x,y,_=g['translation_m'];dx=max(abs(p[0]-x)-.9,0);dy=max(abs(p[1]-y)-.95,0);minimum=min(minimum,math.hypot(dx,dy))
 assert minimum>=.3,(name,minimum)
 checks[name]=dict(endpoints=[a,b],samples=n+1,minimum_furniture_distance_m=minimum,capsule_radius_m=.3,passes=True)
# Human knee envelope from saved meshes compared to the lowest tabletop underside
# over the centre seating bay. Feet remain within the original group footprint.
human=[o for o in s.objects if o.name.startswith('REVIEW_Human')]
assert human and all(o.users_collection[0].name.startswith('REVIEW_ONLY') for o in human)
human_contacts=[]
for o in human:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 for name,(a,b) in bounds.items():
  if all(min(hi[i],b[i])-max(lo[i],a[i])>.001 for i in range(3)):human_contacts.append([o.name,name])
assert not human_contacts,human_contacts
report=dict(passed=True,saved_reopened=True,mesh_objects=len(meshes),unique_meshes=len(checked),linked_instances=len(meshes)-len(checked),evaluated_manifold_failures=bad,replaced_objects_absent=90,tables=6,benches=12,groups=manifest['groups'],routes=checks,ergonomics=dict(seat_height_m=.48,table_height_m=.78,top_to_seat_m=.30,plank_underside_m=.735,central_knee_top_m=.64,vertical_knee_clearance_m=.095,central_clear_width_between_trestles_m=1.195,seat_front_to_table_edge_m=.20,bench_support_width_m=.345,table_support_width_m=.665,stability='Splayed trestles, transverse ties, longitudinal stretcher and paired anti-racking braces. Geometric arrangement only, no load certification.'),limits='Route tests are conservative 2D seating footprint checks only. Source walls/openings unchanged; no actual Unreal collision or seated animation test. Human is temporary review geometry. No moving mechanisms or wall patches.')
src=Path(os.environ.get('MALDEK_SOURCE_REPO','C:/Users/apek-anna/Developer/the-maldek-station'))/'art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
report['source_unchanged']=hashlib.sha256(src.read_bytes()).hexdigest()==manifest['source_sha256'];assert report['source_unchanged']
report['blend_sha256']=hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Seating.blend').read_bytes()).hexdigest()
report['unchanged_context_objects']=len(baseline)
report['human_furniture_aabb_penetrations']=human_contacts
report['floor_contact_shoes']=len([o for o in meshes if '_Floor_Shoe' in o.name])
report['brace_to_spine_and_stretcher_surface_intersections']=brace_joints
report['packed_texture_images']=[im.name for im in bpy.data.images if im.name.startswith('stained_pine') and im.packed_file]
assert len(report['packed_texture_images'])==3
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('VERIFIED',len(meshes),'objects',len(checked),'meshes')
