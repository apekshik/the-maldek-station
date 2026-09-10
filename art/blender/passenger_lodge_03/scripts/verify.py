import bpy,json,hashlib,bmesh,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];f=OUT/'Maldek_Passenger_Lodge_Materials.blend'
bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
r=json.loads((OUT/'material_report.json').read_text());assert r['source_unchanged']
bad=[];count=0
for cn in ['PL03_Open_Grating','PL03_Corrugated_Exterior','PL03_Furniture_Details','PL03_Removable_Roof']:
 for o in bpy.data.collections[cn].objects:
  bm=bmesh.new();bm.from_mesh(o.data)
  if any(not e.is_manifold for e in bm.edges):bad.append(o.name)
  bm.free();count+=1
assert not bad,bad[:5]
def foot(p):
 for dx in [i*.005 for i in range(-16,17)]:
  for dy in [-.06,0,.06]:
   hit,loc,_,_,o,_=s.ray_cast(dg,Vector(p)+Vector((dx,dy,2.05)),Vector((0,0,-1)),distance=2.2)
   if hit and abs(loc.z-p[2])<.07:return True
 return False
routes={'Entry':[[-23.1,-14.3,4],[-17.1,-14.3,4],[-17.1,-6.8,4]],'Platform':[[-17.1,-6.8,4],[-17.1,5.5,4],[-4,5.5,4]],'Bypass':[[-17.1,-14.3,4],[-9.1,-14.3,4],[-9.1,-6.6,4],[-3.5,-6.6,4]],'West':[[-28,-14,4],[-28,5.5,4]]}
samples=0
for name,ps in routes.items():
 for a,b in zip(ps,ps[1:]):
  N=max(1,math.ceil(math.dist(a,b)/.25))
  for i in range(N+1):
   p=Vector(a).lerp(Vector(b),i/N);assert foot(p),(name,list(p));samples+=1
for i in range(24):assert foot((-7.2,-14.42+(i+.5)*.28,(i+1)*4/24)),i
for z in [4.3,4.9,5.7]:
 hit,_,_,_,o,_=s.ray_cast(dg,Vector((-9.5,-6.6,z)),Vector((1,0,0)),distance=6)
 assert not hit,('Right access',o.name)
open_count=0
for i in range(20):
 for j in range(20):
  hit,*_=s.ray_cast(dg,Vector((-28.7+i*.023,-10.8+j*.023,4.02)),Vector((0,0,-1)),distance=.10)
  open_count+=not hit
assert open_count>100,open_count
result={'passed':True,'saved_reopened':True,'new_manifold_meshes':count,'route_foot_patch_samples':samples,'stair_treads_checked':24,'right_access_clear':True,'grating_open_rays_of_400':open_count,'source_unchanged':True,'blend_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'limits':'Blender sampled checks; no Unreal collision, structural engineering or finished prop-detail validation.'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2));print(result)
