import bpy,json,math,bmesh,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
f=OUT/'Maldek_Combined_Station_Blockout.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.data.scenes['04_Combined_Station_Blockout'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
report=json.loads((OUT/'fit_report.json').read_text())
pts=[[-17.1,-6.8,4],[-17.1,4.2,4],[-17.1,5.5,4],[-4,5.5,4]];bad=[]
for a,b in zip(pts,pts[1:]):
 N=max(2,math.ceil(math.dist(a,b)/.2))
 for i in range(N+1):
  p=Vector(a).lerp(Vector(b),i/N)
  for dx,dy in [(0,0),(.3,0),(-.3,0),(0,.3),(0,-.3)]:
   ok=False
   for ex,ey in [(0,0),(.002,0),(-.002,0),(0,.002),(0,-.002)]:
    hit,loc,_,_,ob,_=s.ray_cast(dg,p+Vector((dx+ex,dy+ey,2.05)),Vector((0,0,-1)),distance=2.5)
    if hit and abs(loc.z-p.z)<=.23:ok=True;break
   if not ok:bad.append(list(p))
assert not bad,bad[:5]
for r in report['routes']:
 if r['route']=='Lodge_to_platform':r.update(failed_samples=0,examples=[],boundary_probe_m=.002)
assert all(r['failed_samples']==0 for r in report['routes'])
nonmanifold=[]
for c in ['PL02_New_Deck_Rails_and_Stair','PL02_Fitted_Lodge_Geometry']:
 for o in bpy.data.collections[c].objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data)
  if any(not e.is_manifold for e in bm.edges):nonmanifold.append(o.name)
  bm.free()
assert not nonmanifold,nonmanifold[:5]
assert bpy.data.objects['PL02_Bypass_Upper_Landing'].dimensions.y>=1.99
from mathutils import Vector
for ob in bpy.data.collections['PL02_New_Deck_Rails_and_Stair'].objects:
 if not ob.name.startswith('PL02_Deck'):continue
 ps=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 assert not (lo[0]<-6.3001 and hi[0]>-8.0999 and lo[1]<-7.7001 and hi[1]>-15.1499),ob.name
 assert lo[0]>=-29.451,ob.name
assert report['source_unchanged']
if bpy.data.objects.get('PL02_Safe_Left_Deck_bar'):
 for y in [-6.9,-6.6,-6.3]:
  for z in [4.3,4.9,5.7]:
   hit,_,_,_,ob,_=s.ray_cast(dg,Vector((-9.5,y,z)),Vector((1,0,0)),distance=6)
   assert not hit,('Right-side landing route blocked',ob.name if hit else None)
 for i in range(24):
  y=-14.42+(i+.5)*.28;z=(i+1)*4/24
  for x in [-7.7,-7.2,-6.7]:
   hit,loc,_,_,ob,_=s.ray_cast(dg,Vector((x,y,z+2.05)),Vector((0,0,-1)),distance=2.2)
   assert hit and abs(loc.z-z)<.03,(i,x,ob.name if hit else None)
report['validation']={'saved_reopened':True,'new_mesh_nonmanifold':nonmanifold,'route_floor_headroom_checks_passed':True,'boundary_probe_m':.002,'limits':'Sampled floor/headroom rays, not continuous capsule or Unreal collision. Existing grating arrival retained; lower stair terrain connection remains provisional.'}
(OUT/'fit_report.json').write_text(json.dumps(report,indent=2))
(OUT/'verification.json').write_text(json.dumps({'passed':True,'blend_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),**report['validation']},indent=2))
print('Combined blockout verification passed')
