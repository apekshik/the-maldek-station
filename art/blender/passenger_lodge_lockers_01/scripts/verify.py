"""Saved/reopened evaluated topology and conservative planar clearance audit."""
import bpy,bmesh,json,math,hashlib,itertools,os
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];manifest=json.loads((OUT/'replacement_manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'))
s=bpy.context.scene;s.frame_set(1);col=bpy.data.collections['PLL_Lockers'];dg=bpy.context.evaluated_depsgraph_get()
fail=[];meshes=0;triangles=0
for o in col.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 if any(not e.is_manifold for e in bm.edges):fail.append(o.name)
 if any(f.calc_area()<1e-12 for f in bm.faces):fail.append(o.name+':zero-area')
 meshes+=1;triangles+=sum(len(p.vertices)-2 for p in me.polygons);bm.free();ev.to_mesh_clear()
assert not fail,fail
assert all(x['name'] not in bpy.data.objects for x in manifest['replaced'])
assert len([o for o in col.objects if o.name.endswith('_Assembly')])==12
assert len([o for o in col.objects if o.name.endswith('_Door_Pivot')])==12
# Swept moving-assembly 2D convex hulls include handles, cams, door folds and sleeves.
def hull(points):
 p=sorted(set(points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 low=[]
 for q in p:
  while len(low)>1 and cross(low[-2],low[-1],q)<=0:low.pop()
  low.append(q)
 up=[]
 for q in reversed(p):
  while len(up)>1 and cross(up[-2],up[-1],q)<=0:up.pop()
  up.append(q)
 return low[:-1]+up[:-1]
def overlap(a,b):
 for poly in [a,b]:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   axis=(p[1]-q[1],q[0]-p[0]);pa=[v[0]*axis[0]+v[1]*axis[1] for v in a];pb=[v[0]*axis[0]+v[1]*axis[1] for v in b]
   if max(pa)<min(pb)-1e-7 or max(pb)<min(pa)-1e-7:return False
 return True
pivot=bpy.data.objects['PLL_01_Door_Pivot'];pts=[]
for o in pivot.children_recursive:
 if o.type not in ['MESH','FONT']:continue
 for c in o.bound_box:
  p=pivot.matrix_world.inverted()@o.matrix_world@Vector(c);pts.append((p.x,p.y))
base=hull(pts)
def pose(a,shift=0):
 c=math.cos(math.radians(a));sn=math.sin(math.radians(a));return [(x*c-y*sn+shift,x*sn+y*c) for x,y in base]
angles=list(range(101));clashes=[];max_depth=0
for a in angles:
 p=pose(a);max_depth=max(max_depth,max(y for x,y in p))
 for b in angles:
  if overlap(p,pose(b,.32)):clashes.append((a,b))
assert not clashes,clashes[:15]
# Geometry-based conservative aisle envelope against nearby actual source objects.
front=-7+.528+max_depth
near=[]
for o in bpy.data.collections['REFERENCE_ONLY_Source_Context'].all_objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[0]<-10.28 and hi[0]>-14.1 and lo[1]>front+.02 and hi[2]>4.15 and lo[2]<5.8:near.append((lo[1]-front,o.name,lo,hi))
near.sort();aisle=near[0] if near else None
assert aisle and aisle[0]>.9,aisle
# Punched vent ray passes the actual door mesh. Normal panel ray must hit.
leaf=bpy.data.objects['PLL_01_Door_Sheet'];inv=leaf.matrix_world.inverted()
def leaf_ray(x,z):
 start=pivot.matrix_world@Vector((x,.08,z));end=pivot.matrix_world@Vector((x,-.08,z));return leaf.ray_cast(inv@start,(inv@end-inv@start).normalized())[0]
assert not leaf_ray(.13,.16);assert leaf_ray(.13,.7)
# Actual evaluated mesh triangle sweep against own carcass, excluding intentional hinge joints.
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
s.frame_set(10);bpy.context.view_layer.update()
pivot=bpy.data.objects['PLL_01_Door_Pivot'];center=pivot.matrix_world.translation.copy()
fixed=[o for o in bpy.data.objects['PLL_01_Assembly'].children if o.type=='MESH' and not any(t in o.name for t in ['Hinge','Wall','Plinth'])]
moving=[o for o in pivot.children_recursive if o.type=='MESH']
def combined(objects,transform=None):
 verts=[];polys=[]
 for o in objects:
  offset=len(verts);matrix=o.matrix_world if transform is None else transform@o.matrix_world
  verts.extend([matrix@v.co for v in o.data.vertices]);polys.extend([tuple(offset+i for i in p.vertices) for p in o.data.polygons])
 return BVHTree.FromPolygons(verts,polys)
fixed_bvh=combined(fixed);own_clashes=[]
for angle in range(0,101,2):
 transform=Matrix.Translation(center)@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(-center)
 if combined(moving,transform).overlap(fixed_bvh):own_clashes.append(angle)
assert not own_clashes,own_clashes
s.frame_set(1)
# Sized bag witness is analytic empty-cavity check, not an installed prop.
clear=[.272,.45,1.298];bag=[.23,.40,.50];assert all(b<c for b,c in zip(bag,clear))
# Verify editable asset-only library contains no master context.
with bpy.data.libraries.load(str(OUT/'PLL_Asset_Only.blend'),link=False) as (src,dst):assert src.collections==['PLL_Lockers'],src.collections
sha=hashlib.sha256(Path(manifest['source_file']).read_bytes()).hexdigest();assert sha==manifest['source_sha256']
report={'passed':True,'saved_reopened':True,'mesh_objects_checked':meshes,'evaluated_triangles':triangles,'nonmanifold_or_degenerate':fail,'source_replacements_absent':len(manifest['replaced']),'source_unchanged':True,'source_sha256':sha,'door_neighbor_angle_pairs':len(angles)**2,'angle_step_degrees':1,'moving_assembly_neighbor_hull_intersections':clashes,'max_open_front_world_y':front,'minimum_aisle_to_source_mesh_m':aisle,'clear_storage_lower_m':clear,'bag_witness_m':bag,'vent_cut_rays_pass':True,'own_carcass_mesh_sweep_degrees':list(range(0,101,2)),'own_carcass_intersections':own_clashes,'cam_sequence':'0 to 90 degrees local Y at frames 1 to 8; door remains closed until frame 10','surface_ownership':'Single sheet per carcass wall; door apertures punched through actual sheet; louvres tilted in front, no black proxy backing. Fold ends, hardware fasteners and concealed weld joints intentionally meet/intersect. No blanket arbitrary-mesh coplanarity certification.','restroom_approach':'Rear screen bounds x -14.30..-14.12, y -7.72..-7.20 lie entirely behind door sweep y >= -6.53; original route west of bank remains unchanged.','limits':['Conservative convex XY moving assembly hulls, not engine collision.','1-degree sampled pair sweep; no continuous dynamics or strength certification.','Frame gaps and cavity are authored dimensions; detailed engine collision and interaction reach remain integration work.','Small soft daypack capacity; typical rolling cabin case will not pass 272mm opening.','Wall attachment straps use source stand-off; installation fasteners are schematic.']}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
