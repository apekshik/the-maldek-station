import bpy,json
from mathutils import Vector
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend')
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
out=[]
for o in s.objects:
 if 'Locker' in o.name or ('FIT_' in o.name and any(q in o.name.lower() for q in ['bench','screen','wall','partition'])):
  p=[o.matrix_world@Vector(c) for c in o.bound_box];out.append({'name':o.name,'lo':[min(v[i] for v in p) for i in range(3)],'hi':[max(v[i] for v in p) for i in range(3)],'type':o.type,'collections':[c.name for c in o.users_collection]})
Path(__file__).resolve().parents[1].joinpath('source_inventory.json').write_text(json.dumps({'objects':out,'materials':[m.name for m in bpy.data.materials]},indent=2))
