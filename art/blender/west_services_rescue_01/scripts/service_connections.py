import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
spec=[('Heater_conduit_return',(3.99,4.755,.36),(4.14,4.755,.36),.01,'WSR_Galvanized_steel'),('Handset_return_0',(5.48,4.58,1.285),(5.507,4.58,1.25),.006,'WSR_Graphite_rubber'),('Handset_return_1',(5.48+.027*math.cos(8.1),4.58+.027*math.sin(8.1),.98),(5.39,4.58,1.01),.006,'WSR_Graphite_rubber'),('Handset_return_2',(5.39,4.58,1.01),(5.34,4.58,1.32),.006,'WSR_Graphite_rubber')]
for file in ['Maldek_Rescue_Hut_Editable.blend','Maldek_Rescue_Hut_Fitted_Review.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(P/file)); C=bpy.data.collections['WSR_ASSETS'];root=bpy.data.objects.get('REVIEW_ONLY_WSR_Assembly')
 for n,a,b,r,m in spec:
  if 'WSR_'+n in C.objects:continue
  a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name='WSR_'+n
  for c in list(o.users_collection):c.objects.unlink(o)
  C.objects.link(o);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(bpy.data.materials[m]);mod=o.modifiers.new('Edge radius','BEVEL');mod.width=min(.002,r*.2);mod.segments=2
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
  if root:o.parent=root
  o['surface_owner']='WSR package: '+o.name
 bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/file))
print('SERVICE CONNECTIONS COMPLETE')
