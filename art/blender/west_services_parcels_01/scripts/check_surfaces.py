import bpy,json
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Office.blend'));bpy.context.scene.frame_set(1)
groups=defaultdict(list)
for o in bpy.data.collections['WSP_ASSETS'].objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();mw=ev.matrix_world
 for f in me.polygons:
  n=mw.to_3x3()@f.normal;axis=max(range(3),key=lambda i:abs(n[i]))
  if abs(n[axis])<.999999:continue
  pts=[mw@me.vertices[i].co for i in f.vertices];plane=sum(v[axis] for v in pts)/len(pts);ax=[i for i in range(3) if i!=axis]
  b=[min(v[ax[0]] for v in pts),max(v[ax[0]] for v in pts),min(v[ax[1]] for v in pts),max(v[ax[1]] for v in pts)]
  # Only rectangular main faces: avoid circle/triangle AABB false positives.
  if len(pts)!=4:continue
  groups[(axis,1 if n[axis]>0 else -1,round(plane,5))].append((o.name,f.index,b))
 ev.to_mesh_clear()
hits=[]
for plane,faces in groups.items():
 for i,(an,ai,a) in enumerate(faces):
  for bn,bi,b in faces[i+1:]:
   if an==bn:continue
   w=min(a[1],b[1])-max(a[0],b[0]);h=min(a[3],b[3])-max(a[2],b[2])
   if w>1e-5 and h>1e-5 and w*h>1e-7:hits.append({'a':[an,ai],'b':[bn,bi],'plane':plane,'projected_overlap_m2':w*h})
r={'scope':'Cross-object same-facing coplanar rectangular faces, evaluated meshes, 10 micrometre plane buckets. Rotated/curved and text surfaces excluded; complements targeted fitted BVH checks and visual review.','candidates':hits,'passed':not hits}
(P/'surface_verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
