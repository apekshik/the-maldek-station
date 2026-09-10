import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'weathering'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen_Weathered.blend'))
s=bpy.data.scenes['PLK_Fitted_Review'];bpy.context.window.scene=s
s.cycles.samples=48;s.render.resolution_x=1400;s.render.resolution_y=1050
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in p.devices):s.cycles.device='GPU'
except Exception as e:print(e)
for cam in sorted([o for o in s.objects if o.type=='CAMERA' and o.name.startswith('PLK_REVIEW_')],key=lambda o:o.name):
 s.frame_set(40 if '08_Open' in cam.name else 1)
 bpy.data.collections['PLK_REVIEW_Access'].hide_render='06_Overhead' not in cam.name
 s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
 print('RENDERED',cam.name,flush=True)
