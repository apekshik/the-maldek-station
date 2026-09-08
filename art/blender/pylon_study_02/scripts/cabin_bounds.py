import bpy
from pathlib import Path
from mathutils import Vector
with bpy.data.libraries.load(str(Path('art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend').resolve()),link=False) as (a,b):b.collections=['12_Gondola','VF06_Gondola_Details']
for c in b.collections:
 bpy.context.scene.collection.children.link(c)
 bpy.context.view_layer.update()
 for o in c.all_objects:
  if o.type=='MESH':
   pts=[o.matrix_world@Vector(v) for v in o.bound_box]
   lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
   if 'Hanger' in o.name or hi[2]>7.5:print(o.name,lo,hi)
