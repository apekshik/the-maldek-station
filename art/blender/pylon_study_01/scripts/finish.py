import bpy
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Modern_Twin_Pylon.blend'),load_ui=False)
for o in bpy.data.objects:
 o.name=o.name.replace('Service_hatch_frame','Electrical_enclosure_frame').replace('Service_hatch_leaf','Electrical_enclosure_cover').replace('Hatch_handle','Enclosure_handle')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.region_3d.view_distance=75
   area.spaces.active.region_3d.view_location=Vector((0,0,22))
   area.spaces.active.shading.type='SOLID'
   area.spaces.active.shading.color_type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Maldek_Modern_Twin_Pylon.blend'))
