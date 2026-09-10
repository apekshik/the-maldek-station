import bpy,json,math
from mathutils.bvhtree import BVHTree
from pathlib import Path
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Passenger_Lodge_Kitchen.blend'))
s=bpy.data.scenes['PLK_Fitted_Review'];bpy.context.window.scene=s;s.frame_set(1)
assets=bpy.data.collections['PLK_Assets'];obs=[o for o in assets.all_objects if o.type=='MESH']
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=.00001)
static={o:tree(o) for o in obs};res=[]
for p in assets.all_objects:
 if p.get('motion')!='hinge':continue
 moving=[o for o in p.children_recursive if o.type=='MESH'];hits={}
 for angle in [math.copysign(a,p['open_degrees']) for a in range(5,int(abs(p['open_degrees']))+1,5)]:
  p.rotation_euler.z=math.radians(angle);bpy.context.view_layer.update()
  for o in moving:
   tr=tree(o)
   for q,bv in static.items():
    if q in moving:continue
    if tr.overlap(bv):hits.setdefault(str(angle),set()).add((o.name,q.name))
 p.rotation_euler.z=0;bpy.context.view_layer.update()
 res.append({'pivot':p.name,'candidate_contacts':{a:sorted(v) for a,v in hits.items()}})
for p in assets.all_objects:
 if p.get('motion') not in ['slide','lift']:continue
 moving=[o for o in p.children_recursive if o.type=='MESH'];hits={};closed=p.location.copy();axis=1 if p['motion']=='slide' else 2
 for step in range(1,11):
  travel=p['open_metres']*step/10;p.location[axis]=closed[axis]+travel;bpy.context.view_layer.update()
  for o in moving:
   tr=tree(o)
   for q,bv in static.items():
    if q in moving:continue
    if tr.overlap(bv):hits.setdefault(str(round(travel,4)),set()).add((o.name,q.name))
 p.location=closed;bpy.context.view_layer.update();res.append({'pivot':p.name,'candidate_contacts':{a:sorted(v) for a,v in hits.items()}})
(out/'mechanism_contacts.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
