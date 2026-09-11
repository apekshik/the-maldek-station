import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Emergency_Power_Fitted.blend'));A=json.loads((P/'assembly.json').read_text())
for m in A['mechanisms']:
 if 'Door_hinge' in m['pivot']:bpy.data.objects[m['pivot']].rotation_euler[2]=math.radians(m['open_degrees'])
bpy.context.view_layer.update()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
obs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('WS_BaseWest','WS_BaseEast','WS_BaseNorth','WS_BaseSouth','WSE_Service_door','WSE_Door_jamb','WSE_Door_header','WSE_Battery_case','WSE_Transfer_box','WSE_Distribution_case')):obs.append((o.name,*bounds(o)))
hits=[];path=[(2.9,2.85),(2.9,7.2),(-.65,7.2)]
for a,b in zip(path,path[1:]):
 a,b=Vector(a),Vector(b);N=math.ceil((b-a).length/.05)
 for k in range(N+1):
  p=a.lerp(b,k/N);lo=[p.x-1.25,p.y-.65,.04];hi=[p.x+1.25,p.y+.65,1.8]
  for name,ll,hh in obs:
   if all(min(hi[i],hh[i])-max(lo[i],ll[i])>1e-5 for i in range(3)):hits.append({'obstacle':name,'centre':list(p)})
r={'method':'Sampled 2.50 X x 1.30 Y x 1.76 Z m handling box, 50 mm intervals, local coordinates. Services and projecting control pod removed per handling plan; doors at 90 degrees. Checked against lower walls, finished frame/leaves, battery case, distribution and transfer cabinets.','path_centres':path,'hits':hits,'passed':not hits,'limitation':'Last pose still straddles doorway and walkway. Continuing west exceeds the elevated walk support footprint and requires a separately designed temporary lift/landing. No load-bearing/lifting proof is implied.'};(P/'handling_verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
