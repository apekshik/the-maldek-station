"""Reopen both packages, test real context fit, topology, sweep and combined routes."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];manifest=json.loads((P/'placement_manifest.json').read_text());fail=[]
exec(compile((P/'scripts/verification_helpers.py').read_text(),str(P/'scripts/verification_helpers.py'),'exec'))
def signature(scene):
 data=[]
 for o in sorted(scene.objects,key=lambda o:o.name):
  if o.name.startswith('PLG2_'):continue
  row=[o.name,o.type,[round(v,7) for r in o.matrix_world for v in r]]
  if o.type=='MESH':row.extend([len(o.data.vertices),len(o.data.polygons),[m.name for m in o.data.materials]])
  data.append(row)
 return hashlib.sha256(json.dumps(data).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=manifest['source']);s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;s.frame_set(1);baseline=signature(s)
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_East_Wall_Details.blend'));s=bpy.context.scene;s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();col=bpy.data.collections['PLG2_East_Wall_Details'];checks=[];owned_matrices={o.name:[list(r) for r in o.matrix_world] for o in col.objects}
for o in col.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-14 for f in bm.faces);vol=bm.calc_volume(signed=True);checks.append(dict(name=o.name,nonmanifold=bad,degenerate_faces=deg,volume=vol))
 if bad or deg or vol<=0:fail.append(['topology',o.name,bad,deg,vol])
 bm.free();ev.to_mesh_clear()
images=[dict(name=i.name,packed=bool(i.packed_file),pixels=list(i.size)) for i in bpy.data.images if i.type=='IMAGE']
if any(not x['packed'] for x in images):fail.append(['unpacked_texture'])
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_East_Wall_Details_Fitted.blend'));s=bpy.context.scene;s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();col=bpy.data.collections['PLG2_East_Wall_Details'];ref=bpy.data.collections['PLG2_REFERENCE_ONLY'];context_equal=signature(s)==baseline
if not context_equal:fail.append(['reference_state_changed'])
for name,mat in owned_matrices.items():
 if max(abs(bpy.data.objects[name].matrix_world[i][j]-mat[i][j]) for i in range(4) for j in range(4))>1e-6:fail.append(['transform_mismatch',name])
# Context candidate meshes on the actual evaluated wall, trim, map, bench and locker corner.
context=[]
for o in ref.all_objects:
 if o.type!='MESH' or o.hide_render:continue
 lo,hi=bounds([o.matrix_world@Vector(v) for v in o.bound_box])
 if hi[0]<-11.2 or lo[0]>-10.0 or hi[1]<-6.5 or lo[1]>.1 or hi[2]<4.6 or lo[2]>6.5:continue
 v,f=geom(o);context.append((o.name,bounds(v),BVHTree.FromPolygons(v,f)))
mount_hits=[];minwall=999;max_rack_projection=0
for o in col.objects:
 if o.type!='MESH':continue
 v,f=geom(o);bb=bounds(v);minwall=min(minwall,-10.28-bb[1][0]);tree=None
 if o.name.startswith(('PLG2_Rack','PLG2_Pocket','PLG2_Leaflet_')):max_rack_projection=max(max_rack_projection,-10.28-bb[0][0])
 for n,b,t in context:
  if overlaps(bb,b):
   if tree is None:tree=BVHTree.FromPolygons(v,f)
   if tree.overlap(t):mount_hits.append([o.name,n])
if mount_hits:fail.append(['context_overlap',mount_hits[:10]])
if minwall<0:fail.append(['wall_penetration',minwall])
if max_rack_projection>.16:fail.append(['rack_projection',max_rack_projection])
# Cabinet true vertical hinge sweep, own fixed frame and integrated furniture.
pivot=bpy.data.objects['PLG2_Cabinet_LeafPivot'];pivot.animation_data_clear();moving=[o for o in pivot.children_recursive if o.type=='MESH'];fixed=context[:]
for o in col.objects:
 if o.type!='MESH' or o in moving or 'hinge' in o.name.lower():continue
 v,f=geom(o);fixed.append((o.name,bounds(v),BVHTree.FromPolygons(v,f)))
sweep=[]
for angle in range(0,96,5):
 pivot.rotation_euler.y=math.radians(-angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for o in moving:
  if 'hinge' in o.name.lower():continue
  v,f=geom(o);bb=bounds(v);tree=None
  for n,b,t in fixed:
   if 'hinge' in n.lower():continue
   if overlaps(bb,b):
    if tree is None:tree=BVHTree.FromPolygons(v,f)
    if tree.overlap(t):sweep.append([angle,o.name,n])
if sweep:fail.append(['cabinet_sweep',sweep[:10]])
# All original 15 combined routes plus three east-wall routes, both cabinet states.
pivot.rotation_euler.y=0;s.frame_set(1);closed={o.name:o.matrix_basis.copy() for o in bpy.data.collections['PLK_Assets'].all_objects};s.frame_set(100)
for name,mat in closed.items():
 o=s.objects[name]
 if o.animation_data:o.animation_data_clear()
 o.matrix_basis=mat
assets={o.name for name in ['PLW_Assets','PLD_ASSETS','PLR_Assets','PLK_Assets','PLS_Seating_Kit','PLL_Lockers','PLG_Wall_Details','PLG2_East_Wall_Details'] for o in bpy.data.collections[name].all_objects}
routes=json.loads((P/'routes_input.json').read_text());routechecks=[]
for opened in [False,True]:
 pivot.rotation_euler.y=math.radians(-95 if opened else 0);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();obstacles=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render or (o.name not in assets and not o.name.startswith(('FIT_','PL03_','PLSH_'))):continue
  lo,hi=bounds([o.matrix_world@Vector(v) for v in o.bound_box])
  if hi[2]<=4.12 or lo[2]>=5.8 or hi[0]<-29 or lo[0]>-9 or hi[1]<-15 or lo[1]>6:continue
  v,f=geom(o);poly=hull(v)
  if len(poly)>2:obstacles.append((o.name,lo,hi,poly))
 for name,pts in routes.items():
  nearest=(999,None);count=0
  for a,b in zip(pts,pts[1:]):
   N=max(1,math.ceil(math.dist(a,b)/.025))
   for i in range(N+1):
    x=a[0]+(b[0]-a[0])*i/N-24.1;y=4-a[1]-(b[1]-a[1])*i/N;count+=1
    for on,lo,hi,poly in obstacles:
     if x<lo[0]-1 or x>hi[0]+1 or y<lo[1]-1 or y>hi[1]+1:continue
     d=polygon_distance(x,y,poly)
     if d<nearest[0]:nearest=(d,on)
  row=dict(name=name,cabinet_open=opened,radius=.34,height=1.8,samples=count,minimum_distance=nearest[0],nearest=nearest[1],passed=nearest[0]>=.34);routechecks.append(row)
  if not row['passed']:fail.append(['route',name,opened,nearest])
report=dict(passed=not fail,failures=fail,saved_reopened=True,source_hash_unchanged=hashlib.sha256(Path(manifest['source']).read_bytes()).hexdigest()==manifest['source_sha256'],reference_transform_mesh_count_material_signature_equal=context_equal,mesh_checks=checks,packed_images=images,context_intersections=mount_hits,minimum_wall_separation_m=minwall,rack_maximum_projection_m=max_rack_projection,cabinet_sweep_degrees=list(range(0,96,5)),cabinet_sweep_hits=sweep,combined_routes=routechecks,limits='Sampled Blender evaluated BVH intersections and conservative XY hull walking envelope. Hinge mating hardware excluded. No engine collision, continuous simulation or gameplay validation.')
(P/'verification.json').write_text(json.dumps(report,indent=2));print('VERIFIED',report['passed'],'failures',fail[:8]);assert not fail
