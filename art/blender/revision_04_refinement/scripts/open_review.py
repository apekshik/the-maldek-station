"""Set an isolated gondola material-preview view in a newly opened UI session.
No file save and no geometry changes.
"""
import bpy
from mathutils import Vector
def focus():
 s=bpy.context.scene
 bpy.context.window.view_layer=s.view_layers['02_Full_Shell']
 for o in bpy.context.selected_objects:o.select_set(False)
 parts=[o for o in bpy.data.collections['12_Gondola'].objects if o.type=='MESH' and not o.hide_render]
 for o in parts:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 for area in bpy.context.screen.areas:
  if area.type!='VIEW_3D':continue
  region=next(r for r in area.regions if r.type=='WINDOW')
  with bpy.context.temp_override(area=area,region=region):
   bpy.ops.view3d.localview(frame_selected=False)
  space=area.spaces.active;space.shading.type='MATERIAL'
  space.region_3d.view_location=(0,8.05,5.6)
  space.region_3d.view_distance=12
  space.region_3d.view_rotation=(Vector((0,8,5.2))-Vector((-8,1,7.8))).to_track_quat('-Z','Y')
  space.region_3d.view_perspective='PERSP'
 for o in parts:o.select_set(False)
 return None
bpy.app.timers.register(focus,first_interval=1.0)
