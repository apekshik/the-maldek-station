import bpy,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Control_Door_Study.blend'))
s=bpy.context.scene;s.frame_set(1)
c=bpy.data.collections.new('92_Frost_transmission_review_only');s.collection.children.link(c)
def material(n,color):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);return m
dark=material('Review_silhouette',(.015,.024,.025));back=material('Review_backlight',(.8,.78,.68));p=back.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.87,.66,1);p.inputs['Emission Strength'].default_value=.7
def move(o):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
bpy.ops.mesh.primitive_cube_add(size=1,location=(.65,.6,1.48));o=bpy.context.object;o.name='Review_torso';o.dimensions=(.38,.16,.53);o.data.materials.append(dark);move(o)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.12,location=(.65,.6,1.91));o=bpy.context.object;o.name='Review_head';o.scale=(.8,.8,1.1);o.data.materials.append(dark);move(o)
bpy.ops.mesh.primitive_cube_add(size=1,location=(.65,1.2,1.75));o=bpy.context.object;o.name='Review_light_background';o.dimensions=(1.15,.02,1.1);o.data.materials.append(back);move(o)
# Soft transmission rather than opacity; roughness remains editable in one material.
gp=bpy.data.materials['D01_Frosted_glass'].node_tree.nodes.get('Principled BSDF');gp.inputs['Roughness'].default_value=.32
s.camera=bpy.data.objects['01_Closed'];s.cycles.samples=64
s.render.filepath=str(OUT/'previews/06_Frosted_transmission.png');bpy.ops.render.render(write_still=True)
c.hide_render=True;c.hide_viewport=True
s.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Control_Door_Study.blend'))
for n in ['01_Closed','02_Open','03_Hardware','04_In_building','05_Interior']:
 s.camera=bpy.data.objects[n];s.frame_set(90 if n=='02_Open' else 1)
 context=bpy.data.collections['91_Existing_control_building'];context.hide_render=n!='04_In_building';context.hide_viewport=n!='04_In_building';bpy.data.collections['03_Review_frame'].hide_render=n=='04_In_building'
 s.render.filepath=str(OUT/'previews'/f'{n}.png');bpy.ops.render.render(write_still=True)
