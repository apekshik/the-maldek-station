import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1];s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();checks=[]
def hit(p,d,l):return s.ray_cast(deps,Vector(p),Vector(d),distance=l)
def add(n,v,**kw):checks.append(dict(check=n,passed=bool(v),**kw))
for i in range(20):
 x=.19+i*.28;z=(i+1)*3.65/20;r=hit((x,-1.1,z+.1),(0,0,-1),.15)
 add('Stair tread height',r[0] and abs(r[1].z-z)<.015)
 add('Stair headroom',not hit((x,-1.1,z+.04),(0,0,1),2)[0])
for y in [-1,.1,.9,1.5,2.3]:
 r=hit((5.96,y,3.9),(0,0,-1),.3);add('Upper landing floor',r[0] and abs(r[1].z-3.65)<.015)
 add('Upper access headroom',not hit((5.96,y,3.70),(0,0,1),1.95)[0])
for x,y in [(7.8,y) for y in [-4,-2,0,2,4,6,7.2]]+[(x,7.2) for x in [-9,-6,-3,0,3,6]]+[(x,-5.3) for x in [-9,-6,-3,0,3,6]]:
 for z in [.4,1,1.7]:
  for i in range(8):add('Promenade 1.2m diameter clearance',not hit((x,y,z),(math.cos(i*math.pi/4),math.sin(i*math.pi/4),0),.6)[0])
def coverage(y):
 count=0
 for i in range(19):
  for j in range(11):count+=hit((1.73+i*.021,y+j*.019,.035),(0,0,-1),.065)[0]
 return count/209
inner=coverage(5.59);middle=coverage(6.4);outer=coverage(8.56)
add('Inner ring has real openings',inner<.65,coverage=inner)
add('Broad middle ring is solid',middle>.95,coverage=middle)
add('Outer ring has real openings',outer<.65,coverage=outer)
for o in [bpy.data.objects['Interstorey_transfer_slab'],bpy.data.objects['Quarters_Floor']]:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 if o.name=='Interstorey_transfer_slab':slabtop=max(v.z for v in pts);slabbottom=min(v.z for v in pts)
 else:floorbottom=min(v.z for v in pts);floortop=max(v.z for v in pts);front=max(v.y for v in pts)
add('Transfer slab meets upper floor',abs(slabtop-floorbottom)<.001)
add('Transfer slab meets lower wall top',abs(slabbottom-3.15)<.001)
add('Upper floor at intended height',abs(floortop-3.65)<.001)
add('Upper room projects forward',front>6.39)
report={'count':len(checks),'passed':all(c['passed'] for c in checks),'failures':[c for c in checks if not c['passed']],'checks':checks,'limits':'Sampled geometry checks, not Unreal capsule tests or structural validation.'}
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}));assert report['passed']
