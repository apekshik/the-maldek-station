import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Station_Furnished.blend'));s=bpy.context.scene;c=bpy.data.collections['SD_REVIEW_ONLY'];s.frame_set(1)
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100
try:
 pr=bpy.context.preferences.addons['cycles'].preferences;pr.compute_device_type='OPTIX';pr.get_devices()
 for d in pr.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in pr.devices):s.cycles.device='GPU'
except Exception:pass
s.world=bpy.data.worlds.new('SD_ReviewWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.48,.54,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.view_settings.view_transform='AgX'
for n,pos,target,power,size in [('Janitor',(-12.2,-8,6.6),(-10.6,-7.8,5.1),300,2),('Rescue',(-35,2.3,7.1),(-36,4.5,5.8),360,3),('Power',(-34.9,2.1,4.1),(-34.9,4.4,2.2),380,3)]:
 d=bpy.data.lights.new('SD_TEMP_'+n,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('SD_TEMP_Camera');cam=bpy.data.objects.new(d.name,d);c.objects.link(cam);s.camera=cam
(P/'previews').mkdir(exist_ok=True)
shots=[('01_Janitor',(-12.65,-7.92,5.35),(-10.6,-7.80,5.25),22),('02_Janitor_detail',(-11.7,-7.82,5.4),(-10.65,-7.90,5.1),27),('03_Rescue_shelves',(-34.7,2.6,6.25),(-36.15,4.5,5.95),30),('04_Rescue_room',(-32.15,3,6.25),(-35.8,3.35,5.65),23),('05_Power_spares',(-35,1.5,2.85),(-34.65,4.55,2.35),28)]
# Restrict render visibility by view area without discarding source context.
original={o.name:o.hide_render for o in s.objects}
for name,pos,target,lens in shots:
 for ob in s.objects:
  if ob.type in ['MESH','FONT','CURVE']:
   bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
   near=(max(v.x for v in bb)>-15 and min(v.x for v in bb)<-9 and max(v.y for v in bb)>-10 and min(v.y for v in bb)<-6) if 'Janitor' in name else ob.name.startswith(('WS_','WS02_','WSP_','WSR_','WSE_','SD_'))
   ob.hide_render=original[ob.name] or not near
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('REVIEW COMPLETE')
