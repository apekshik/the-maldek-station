"""Saved/reopened evaluated topology, paper layers and layout checks (not engine collision)."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];m=json.loads((P/'replacement_manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Wall_Details.blend'));c=bpy.data.collections['PLG_Wall_Details'];dg=bpy.context.evaluated_depsgraph_get();fail=[];mesh_checks=[];face_keys={};duplicates=[]
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
for o in c.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);deg=sum(f.calc_area()<1e-14 for f in bm.faces)
 if bad or volume<=0 or deg:fail.append([o.name,'topology',bad,volume,deg])
 mesh_checks.append(dict(name=o.name,vertices=len(me.vertices),faces=len(me.polygons),nonmanifold_edges=bad,signed_volume_m3=volume,degenerate_faces=deg))
 for f in me.polygons:
  key=tuple(sorted(tuple(round(x,6) for x in o.matrix_world@me.vertices[i].co) for i in f.vertices))
  if key in face_keys and face_keys[key]!=o.name:duplicates.append([face_keys[key],o.name])
  face_keys[key]=o.name
 bm.free();ev.to_mesh_clear()
if duplicates:fail.append(['coincident_duplicate_faces',duplicates])
# Door/reveal envelopes include a conservative 50 mm safety border, actual source openings.
openings=[('platform',[-17.75,3.0,4],[-16.45,4.3,6.35]),('arrival',[-17.75,-7.5,4],[-16.45,-6.6,6.35]),('restrooms',[-15.75,-7.7,4],[-14.45,-6.6,6.35]),('women',[-14.15,-9.45,4],[-13.15,-8.6,6.25]),('men',[-12.15,-9.45,4],[-11.15,-8.6,6.25]),('staff',[-19.6,-11.05,4],[-18.7,-9.95,6.25])]
opening_hits=[]
for o in c.objects:
 if o.type!='MESH':continue
 lo,hi=bounds(o)
 for name,a,b in openings:
  if all(min(hi[i],b[i])-max(lo[i],a[i])>1e-5 for i in range(3)):opening_hits.append([name,o.name])
if opening_hits:fail.append(['opening_envelope',opening_hits])
routes=[('central',(-17.1,-6.3),(-17.1,3.8),.75),('coffee_queue',(-17.1,-5.7),(-21.5,-5.7),.6),('locker_approach',(-17.1,-5.5),(-11.0,-5.5),.75),('west_secondary',(-22.2,2.5),(-22.2,-5.6),.6),('restroom_corridor',(-15.05,-8.2),(-11.3,-8.2),.6)]
samples=0;hits=[]
for name,a,b,r in routes:
 count=math.ceil(math.dist(a,b)/.1)
 for j in range(count+1):
  x=a[0]+(b[0]-a[0])*j/count;y=a[1]+(b[1]-a[1])*j/count;samples+=1
  for o in c.objects:
   if o.type!='MESH':continue
   lo,hi=bounds(o)
   if hi[2]<=4.05 or lo[2]>=6.1:continue
   dx=max(lo[0]-x,0,x-hi[0]);dy=max(lo[1]-y,0,y-hi[1])
   if dx*dx+dy*dy<r*r:hits.append([name,o.name,j])
if hits:fail.append(['route_samples',hits[:20]])
# Ray sample paper front/back in community-root space to prove overlapping notes are separated.
board=bpy.data.objects['PLG_Community'];notes=[o for o in c.objects if o.name.startswith('PLG_Notice_')];trees=[]
for o in notes:
 transform=board.matrix_world.inverted()@o.matrix_world;vs=[transform@v.co for v in o.data.vertices];trees.append((o.name,BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons],all_triangles=False)))
overlap_samples=0;minimum=1
for xi in range(126):
 for yi in range(90):
  x=-.72+xi*.01;y=-.45+yi*.01;depths=[]
  for name,tree in trees:
   a=tree.ray_cast(Vector((x,y,.1)),Vector((0,0,-1)),.15)[0];b=tree.ray_cast(Vector((x,y,0)),Vector((0,0,1)),.1)[0]
   if a is not None and b is not None:depths.append((b.z,a.z,name))
  if len(depths)>1:
   overlap_samples+=1;depths.sort()
   for low,high in zip(depths,depths[1:]):
    gap=high[0]-low[1];minimum=min(minimum,gap)
    if gap<.00015:fail.append(['paper_separation',low[2],high[2],gap])
assert overlap_samples>0,'No intended notice overlap sampled'
images=[dict(name=i.name,packed=bool(i.packed_file),size=list(i.size)) for i in bpy.data.images if i.type=='IMAGE']
if any(not i['packed'] for i in images):fail.append(['unpacked_images'])
for root in ['PLG_Clock_Hour_pivot','PLG_Clock_Minute_pivot']:
 o=bpy.data.objects[root]
 if abs(o.location.x)>1e-7 or abs(o.location.y)>1e-7:fail.append(['clock_axle',root])
source_unchanged=hashlib.sha256(Path(m['source_file']).read_bytes()).hexdigest()==m['source_sha256']
if not source_unchanged:fail.append(['source_changed'])
# Reopen review file and confirm package transforms persisted identically.
expected={o.name:[list(row) for row in o.matrix_world] for o in c.objects};bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Wall_Details_Fitted.blend'));mismatch=[]
for name,mat in expected.items():
 if name not in bpy.data.objects or max(abs(bpy.data.objects[name].matrix_world[i][j]-mat[i][j]) for i in range(4) for j in range(4))>1e-6:mismatch.append(name)
if mismatch:fail.append(['fitted_transform_mismatch',mismatch])
for n in m['retire_exact']:
 if n in bpy.data.objects and not bpy.data.objects[n].hide_render:fail.append(['proxy_not_retired',n])
report=dict(passed=not fail,failures=fail,saved_reopened=True,owned_objects=len(expected),mesh_checks=mesh_checks,duplicate_faces=duplicates,source_unchanged=source_unchanged,opening_envelopes_checked=openings,opening_hits=opening_hits,walking_route_sample_count=samples,walking_route_hits=hits,notice_overlap_samples=overlap_samples,minimum_notice_gap_m=minimum,packed_images=images,fitted_transform_mismatches=mismatch,limits='New package versus proxy layout envelopes only. No engine collision, interaction, Unreal import or PIE test; exact-face duplicate check does not prove arbitrary intersection freedom.')
(P/'verification.json').write_text(json.dumps(report,indent=2));print('VERIFICATION',report['passed'],'failures',fail[:5],'notice gap',minimum)
assert not fail
