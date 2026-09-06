import bpy,json,time,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
stage=sys.argv[sys.argv.index('--')+1]
s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.refresh_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=40;s.render.resolution_x=1400;s.render.resolution_y=930;s.render.resolution_percentage=100
for layer in s.view_layers:layer.use=layer.name=='02_Full_Shell'
bpy.context.window.view_layer=s.view_layers['02_Full_Shell']
shots=[('night_platform','CAM_R03_Platform_Rain'),('night_controls','CAM_R03_Control_Room')]
report={}
for name,camera in shots:
 s.camera=bpy.data.objects[camera];s.render.filepath=str(OUT/'audit'/stage/f'{name}.png')
 t=time.perf_counter();bpy.ops.render.render(write_still=True,layer='02_Full_Shell');report[name]={'seconds':round(time.perf_counter()-t,3),'camera':camera,'samples':40}
(OUT/'audit'/f'{stage}_night_timings.json').write_text(json.dumps(report,indent=2))
