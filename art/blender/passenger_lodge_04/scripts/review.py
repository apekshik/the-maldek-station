"""Render the saved integrated scene without modifying the delivery file."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Integrated.blend'))
s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
# Temporary, explicitly named review illumination. Exterior source lighting retained.
c=bpy.data.collections['PLI_REVIEW_ONLY']
for x,y,p in [(-21,-9.5,180),(-14.5,-11,100),(-11.6,-11,100),(-14,-8.1,100)]:
 d=bpy.data.lights.new('PLI_TEMP_AREA','AREA');d.energy=p;d.shape='DISK';d.size=1.5;d.color=(1,.86,.69)
 o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=(x,y,6.95)
views=[
 ('01_Exterior_control',(-38,-29,18),(-13,-3,5),40,1,False),
 ('02_Platform_front',(-29,14,9),(-14,0,5.4),28,1,False),
 ('03_Hall',(-22.7,2.4,5.65),(-14,-5.7,5.1),22,1,False),
 ('04_Hall_reverse',(-11.3,-5.1,5.65),(-22,1.7,5.3),22,1,False),
 ('05_Kitchen',(-19.65,-8.6,5.65),(-22.5,-10.7,5.15),19,1,False),
 ('06_Hallway_east',(-15.3,-8.35,5.65),(-11.7,-8.95,5.35),20,1,False),
 ('07_Hallway_west',(-11.4,-8.35,5.65),(-15,-8.6,5.35),20,1,False),
 ('08_Women',(-13.62,-9.75,5.65),(-14.95,-11.55,4.95),19,40,False),
 ('09_Cutaway',(-32,-22,26),(-17,-4,4),38,1,True),
 ('10_Arrival_threshold',(-17.1,-9.2,5.05),(-17.1,-7.15,4.8),28,80,False),
 ('11_Window_inside',(-19.2,1.7,5.6),(-20.8,3.9,5.8),28,1,False),
 ('12_Lockers_open',(-16.6,-3.8,5.65),(-12.5,-6.7,4.9),28,50,False),
 ('13_Hall_dim',(-22.7,2.4,5.65),(-14,-5.7,5.1),22,1,False)]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
roof=bpy.data.collections['PL03_Removable_Roof']
energies={o.name:o.data.energy for o in s.objects if o.type=='LIGHT'}
(OUT/'previews').mkdir(exist_ok=True)
for name,pos,target,lens,frame,cut in views:
 if args and name not in args:continue
 s.frame_set(frame);roof.hide_render=cut
 for o in s.objects:
  if o.type=='LIGHT':o.data.energy=energies[o.name]*(.25 if 'dim' in name else 1)
 d=bpy.data.cameras.new('PLI_TEMP_'+name);o=bpy.data.objects.new(d.name,d);c.objects.link(o)
 o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.02;s.camera=o
 s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
 print('RENDERED',name,flush=True)
(OUT/'review_views.json').write_text(json.dumps(views,indent=2))
