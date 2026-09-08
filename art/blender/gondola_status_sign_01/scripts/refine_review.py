"""Apply the final inspection refinements to an already built study and re-render."""
import bpy,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]
for o in list(bpy.data.objects):
 if o.name.startswith('NS01_Tube_standoff'):bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith('NS01_Row_rule'):
  for old,new in [(2.388,2.415),(2.147,2.185),(1.906,1.940)]:
   if abs(o.location.z-old)<.001:o.location.z=new
runpy.run_path(str(out/'scripts/finish.py'),run_name='sign_finish')['finish']()
s=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for name,cam,frame in [('01_BOARD','NS01_Close_review',1),('02_ARRIVING','NS01_Close_review',49),('03_DEPART','NS01_Close_review',97),('04_AWAY','NS01_Close_review',145),('05_Placement','NS01_Placement_review',1),('06_Rear','NS01_Rear_detail',1)]:
 s.camera=bpy.data.objects[cam];s.frame_set(frame);s.render.filepath=str(out/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['NS01_Close_review'];s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
