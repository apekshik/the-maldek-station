import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Emergency_Power.blend'))
deps=bpy.context.evaluated_depsgraph_get();groups={};pairs={}
def clip(poly,a,b):
 def side(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  sp,sq=side(p),side(q)
  if sp>=-1e-8:out.append(p)
  if (sp>0)!=(sq>0):
   t=sp/(sp-sq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return out
def area(poly):return abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))/2 if poly else 0
for ob in bpy.data.collections['WSE_ASSETS'].objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();M=ev.matrix_world
 for f in me.polygons:
  if f.area<1e-6:continue
  vs=[M@me.vertices[i].co for i in f.vertices];n=(M.to_3x3()@f.normal).normalized();axis=max(range(3),key=lambda i:abs(n[i]));sgn=1 if n[axis]>0 else -1;n=n*sgn;d=n.dot(vs[0]);key=tuple(round(v,5) for v in n)+(round(d,5),)
  axes=[i for i in range(3) if i!=axis];poly=[(v[axes[0]],v[axes[1]]) for v in vs]
  signed=sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))
  if signed<0:poly.reverse()
  lo=[min(v[i] for v in poly) for i in range(2)];hi=[max(v[i] for v in poly) for i in range(2)]
  for name,pp,ll,hh,ss in groups.get(key,[]):
   if name==ob.name or any(min(hi[i],hh[i])-max(lo[i],ll[i])<1e-5 for i in range(2)):continue
   cut=poly[:]
   for a,b in zip(pp,pp[1:]+pp[:1]):
    cut=clip(cut,a,b)
    if not cut:break
   ar=area(cut)
   if ar>1e-6:
    pair=tuple(sorted((name,ob.name)))+(ss==sgn,);pairs[pair]=pairs.get(pair,0)+ar
  groups.setdefault(key,[]).append((ob.name,poly,lo,hi,sgn))
 ev.to_mesh_clear()
result={'method':'Evaluated convex polygon coplanarity buckets (1e-5); 2D convex intersection, positive projected area >1e-6 m2. Asset meshes only; FONT labels omitted. Intentional embedded joints require classification, not blanket dismissal.','pairs':[{'a':a,'b':b,'same_facing':same,'projected_overlap_m2':v} for (a,b,same),v in pairs.items()]}
(P/'surface_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

