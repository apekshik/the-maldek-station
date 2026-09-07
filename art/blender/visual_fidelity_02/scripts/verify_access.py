import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1];s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();checks=[]
def cast(p,d,l):return s.ray_cast(deps,Vector(p),Vector(d),distance=l)
def add(name,passed,**details):checks.append(dict(check=name,passed=bool(passed),**details))
for i in range(20):
 x=.19+i*.28;z=(i+1)*3.35/20
 result=cast((x,-1.1,z+.12),(0,0,-1),.2)
 add('stair tread elevation',result[0] and abs(result[1].z-z)<.015,index=i)
 result=cast((x,-1.1,z+.04),(0,0,1),2.0)
 add('stair vertical headroom',not result[0],index=i,hit=result[4].name if result[0] else None)
for y in [-1.1,-.5,.1,.5,.9,1.3,1.8,2.3,2.6]:
 result=cast((5.96,y,3.6),(0,0,-1),.3)
 add('landing and upstairs floor',result[0] and abs(result[1].z-3.35)<.015,y=y)
 result=cast((5.96,y,3.4),(0,0,1),1.95)
 add('upper entry headroom',not result[0],y=y,hit=result[4].name if result[0] else None)
for x in [5.74,5.95,6.16]:
 for z in [3.4,4.3,5.2]:
  result=cast((x,.3,z),(0,1,0),.8)
  add('upper doorway passage',not result[0],x=x,z=z,hit=result[4].name if result[0] else None)
for x in [4.2,4.65,5.2]:
 for z in [.06,.6,1.7,2.2]:
  result=cast((x,5.6,z),(0,-1,0),.8)
  add('lower doorway passage',not result[0],x=x,z=z,hit=result[4].name if result[0] else None)
for x,y in [(2.7,2.4),(3,3),(4.9,1.9)]:
 result=cast((x,y,3.5),(0,0,-1),.2)
 add('upper floor no roof seam protrusion',result[0] and abs(result[1].z-3.35)<.002,x=x,y=y)
for o in bpy.data.objects:
 if o.name.startswith('Landing_support'):
  top=max((o.matrix_world@Vector(v)).z for v in o.bound_box)
  add('landing support contact',top>=3.306,top_m=top)
report={'checks':checks,'count':len(checks),'passed':all(c['passed'] for c in checks),'scope':'Sampled rays and measured support bounds. Not continuous capsule sweeps or structural engineering validation.','unreal_integration':False}
(out/'access_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'count':len(checks),'passed':report['passed'],'failures':[c for c in checks if not c['passed']]}))
assert report['passed'],'See access_verification.json'
