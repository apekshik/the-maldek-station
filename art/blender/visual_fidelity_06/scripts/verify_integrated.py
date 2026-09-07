"""Geometry regression and sampled walking-space checks; not UE capsule validation."""
import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Integrated_Station.blend'))
s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
report=json.loads((OUT/'integration_report.json').read_text())
checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail})
for name,r in report['unchanged_anchors'].items():check('Unchanged '+name,r['max_error_m']<.0001,r['bounds'])
protected=[[-1.65,1.65,5.05,11.1,'gondola bay'],[6.1,7.9,.4,6.75,'internal descent'],[-13.9,-11.9,-15.7,-9.3,'arrival descent']]
for a,b,c,d,name in protected:
 overlaps=[]
 for r in report['new_deck_rects']:
  x0,x1,y0,y1,z,k=r
  if z==4 and min(b,x1)-max(a,x0)>.001 and min(d,y1)-max(c,y0)>.001:overlaps.append(r)
 check('New deck clears '+name,not overlaps,overlaps)
def ray(p,d,length):
 h,loc,n,i,o,m=s.ray_cast(dg,Vector(p),Vector(d),distance=length)
 return {'object':o.name,'point':list(loc)} if h else None
samples=[('lower entry',(5.25,.8,0)),('lower aisle',(4.3,2,0)),('lower aisle',(4.3,3.9,0)),('drive door',(2,-.1,0)),('lower stores',(2,-3,0)),('boarding approach',(0,4.4,4)),('cabin entry',(0,5.18,4)),('cabin aisle',(0,8,4)),('hall door',(-10.25,-.12,4)),('control door',(-3.3,.15,4)),('control aisle',(-4.1,-2,4)),('hall link',(-8,-3.1,4)),('quarters doorway',(-2.13,-4.5,7.65))]
for n,(x,y,z) in samples:
 floor=ray((x,y,z+.18),(0,0,-1),.5)
 clear=ray((x,y,z+.18),(0,0,1),1.95)
 check(n+' floor',floor is not None,floor)
 check(n+' headroom',clear is None,clear)
# Every original visible stair tread retains its exact transform and dimensions.
orig=json.loads((OUT/'r11_objects.json').read_text())
for r in orig:
 if '06_Stairs_and_Landings' not in r['collections'] or 'Tread' not in r['name'] or r['hide']:continue
 o=bpy.data.objects.get(r['name'])
 if not o:check(r['name'],False,'missing');continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 b=[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
 err=max(abs(b[i][j]-r['bounds'][i][j]) for i in range(2) for j in range(3))
 check(r['name']+' unchanged',err<.0002,err)
check('Three outward material band widths',report['bands_m']==[1.8,3.6,1.95],report['bands_m'])
for name in ['West_canopy_clear_of_quarters','Front_canopy_clear_of_quarters','Canopy_corner_return']:
 o=bpy.data.objects[name];pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 a=[min(p[i] for p in pts) for i in range(3)];b=[max(p[i] for p in pts) for i in range(3)]
 overlap=min(b[0],-1.4)-max(a[0],-7.7)>0 and min(b[1],1.3)-max(a[1],-4.6)>0
 check(name+' clears upper floor',not overlap,[a,b])
out={'scope':'Blender geometry regression and vertical point samples. Does not replace Unreal collision or capsule walkthrough.','checks':checks,'passed':sum(c['pass'] for c in checks),'failed':[c for c in checks if not c['pass']]}
(OUT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'passed':out['passed'],'failures':out['failed']},indent=2))
