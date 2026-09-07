import bpy
from mathutils import Vector
for name,p,t,lens in [('06_Water_Tower',(28,25,12),(18,13.3,3.5),42),('07_Service_Detail',(21,7,4),(15,-.1,1.4),40)]:
 if name in bpy.data.objects:continue
 d=bpy.data.cameras.new(name);d.lens=lens;o=bpy.data.objects.new(name,d)
 bpy.data.collections['Presentation_Only'].objects.link(o);o.location=p
 o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
