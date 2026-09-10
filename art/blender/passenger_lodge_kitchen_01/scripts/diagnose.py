import bpy,bmesh
from pathlib import Path
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Passenger_Lodge_Kitchen.blend'))
for o in bpy.data.collections['PLK_Assets'].all_objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 for e in bm.edges:
  if not e.is_manifold:print(o.name,'faces',len(e.link_faces),'coords',[list(v.co) for v in e.verts])
 bm.free()
