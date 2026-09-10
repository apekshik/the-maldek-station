"""Saved-scene integration checks, including cross-package mechanism sweeps."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1];ART=OUT.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
r=json.loads((OUT/'reconciliation.json').read_text());report={'saved_reopened':True,'failures':[],'topology':[],'cross_package_sweep_hits':[]}
def check(ok,msg):
 if not ok:report['failures'].append(msg)
def bb(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]]
def overlap(a,b):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>1e-5 for i in range(3))
def geom(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[o.matrix_world@p.co for p in m.vertices];f=[list(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def tree(o):
 v,f=geom(o);return BVHTree.FromPolygons(v,f)
for n in r['retired']:check(n not in s.objects,'Retired object remains: '+n)
owner={}
for p in r['packages']:
 col=bpy.data.collections[p['collection']]
 for o in col.all_objects:owner[o.name]=p['kind']
 expected=set(p['objects'])-set(r['retired']);check(set(o.name for o in col.all_objects)==expected,'Collection inventory '+p['kind'])
for n,state in r['final_asset_state'].items():
 o=s.objects.get(n);check(o is not None,'Missing asset '+n)
 if o:check(max(abs(o.matrix_world[i][j]-state['matrix'][i][j]) for i in range(4) for j in range(4))<1e-5,'Transform '+n)
skip=set(r['retired'])|set(r['patched_objects'])|set(x['original'] for x in r['trim_repairs'])
for n,state in r['baseline'].items():
 if n in skip:continue
 o=s.objects.get(n);check(o is not None,'Missing context '+n)
 if o:
  check(max(abs(o.matrix_world[i][j]-state['matrix'][i][j]) for i in range(4) for j in range(4))<1e-5,'Context transform '+n)
  if state['bounds']:check(max(abs(bb(o)[i][j]-state['bounds'][i][j]) for i in range(2) for j in range(3))<1e-5,'Context bounds '+n)
for im in bpy.data.images:
 if im.source=='FILE' and im.users:check(bool(im.packed_file),'Unpacked image '+im.name)
checked=set()
for o in s.objects:
 if o.type!='MESH' or not(o.name in owner or o.name.startswith('PLSH_') or o.name in r['patched_objects']):continue
 key=(o.data.as_pointer(),tuple((m.type,m.show_viewport) for m in o.modifiers))
 if key in checked:continue
 checked.add(key);e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 bad=sum(not x.is_manifold for x in bm.edges);deg=sum(x.calc_area()<1e-12 for x in bm.faces)
 if bad or deg:report['topology'].append({'object':o.name,'nonmanifold':bad,'degenerate':deg})
 bm.free();e.to_mesh_clear()
report['unique_evaluated_meshes']=len(checked)
def animated(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
moving=[o for o in s.objects if o.type=='MESH' and o.name in owner and animated(o)]
static=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or animated(o):continue
 a=bb(o)
 if a[1][0]<-24.3 or a[0][0]>-9.9 or a[1][1]<-13.4 or a[0][1]>4.3 or a[1][2]<4.02 or a[0][2]>7.1:continue
 static.append((o, a, None))
cache={};hitset=set();samples=0
for frame in range(1,102,5):
 s.frame_set(min(frame,100));bpy.context.view_layer.update();current=[(o,bb(o)) for o in moving]
 for o,a in current:
  ot=None
  for other,b,_ in static:
   if owner.get(other.name)==owner[o.name] or not overlap(a,b):continue
   if ot is None:ot=tree(o)
   if other.name not in cache:cache[other.name]=tree(other)
   if ot.overlap(cache[other.name]):hitset.add((o.name,other.name,frame))
  samples+=1
 for i,(o,a) in enumerate(current):
  for other,b in current[i+1:]:
   if owner[o.name]!=owner[other.name] and overlap(a,b) and tree(o).overlap(tree(other)):hitset.add((o.name,other.name,frame))
 print('SWEEP',frame,len(hitset),flush=True)
report['cross_package_sweep_hits']=sorted(hitset);report['moving_mesh_pose_samples']=samples
check(not hitset,'Cross-package sweep intersections')
check(not report['topology'],'Evaluated topology defects')
report['blend_sha256']=hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Integrated.blend').read_bytes()).hexdigest()
report['passed']=not report['failures']
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print('VERIFY',report['passed'],report['failures'][:10],flush=True)
