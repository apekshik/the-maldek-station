import bpy,json,bmesh,itertools
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Editable.blend'))
S=bpy.context.scene; C=bpy.data.collections['WSR_ASSETS']; report={}
for frame in [1,40,80]:
 S.frame_set(frame); bpy.context.view_layer.update(); dep=bpy.context.evaluated_depsgraph_get(); planes={}; errors=[]
 for o in C.objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dep); me=ev.to_mesh(); bm=bmesh.new();bm.from_mesh(me)
  if any(not e.is_manifold for e in bm.edges) or bm.calc_volume(signed=True)<=0:errors.append(o.name)
  bm.free()
  for f in me.polygons:
   n=(ev.matrix_world.to_3x3()@f.normal).normalized(); ax=max(range(3),key=lambda i:abs(n[i]))
   if abs(n[ax])<.999999 or len(f.vertices)!=4:continue
   pts=[ev.matrix_world@me.vertices[i].co for i in f.vertices]; oth=[i for i in range(3) if i!=ax]
   lo=[min(p[i] for p in pts) for i in oth];hi=[max(p[i] for p in pts) for i in oth]
   if abs(f.area-(hi[0]-lo[0])*(hi[1]-lo[1]))>1e-7:continue
   key=(ax,1 if n[ax]>0 else -1,round(sum(p[ax] for p in pts)/4,5));planes.setdefault(key,[]).append((o.name,lo,hi))
  ev.to_mesh_clear()
 dup=[]
 for key,faces in planes.items():
  for a,b in itertools.combinations(faces,2):
   if a[0]!=b[0] and min(min(a[2][i],b[2][i])-max(a[1][i],b[1][i]) for i in range(2))>1e-5:dup.append([a[0],b[0],key])
 report[str(frame)]={'topology_errors':errors,'same_facing_rectangular_coplanar_candidates':dup,'passed':not(errors or dup)}
report['passed']=all(v['passed'] for v in report.values())
(P/'pose_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
