import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/apek-anna/Developer/the-maldek-station/art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend')
for name in ['12_Gondola','VF06_Gondola_Details']:
 for o in bpy.data.collections[name].all_objects:
  if any(k in o.name.lower() for k in ['door','floor','step','threshold']):
   vs=[o.matrix_world@Vector(v) for v in o.bound_box];print('PART',o.name,[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)])
