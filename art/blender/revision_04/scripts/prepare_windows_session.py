"""Create a GPU-configured starting copy; preserve revision 03 and existing work."""
import bpy
from pathlib import Path

out = Path(__file__).resolve().parents[1] / 'millford_v2_detail_04.blend'
if out.exists():
    raise RuntimeError(f'Refusing to overwrite existing work: {out}')
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.refresh_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX' and '5070 Ti' in device.name
assert any(d.use for d in prefs.devices)
bpy.ops.wm.save_userpref()
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.camera = bpy.data.objects['CAM_R03_Platform_Rain']
scene.render.resolution_x = 1400
scene.render.resolution_y = 930
scene.render.resolution_percentage = 100
scene.cycles.samples = 40
scene.render.filepath = str(out.parent / 'audit' / 'before' / 'platform_rain_windows.png')
for layer in scene.view_layers:
    layer.use = layer.name == '02_Full_Shell'
bpy.context.window.view_layer = scene.view_layers['02_Full_Shell']
scene['Status'] = 'Revision 04 starting copy: Windows OptiX baseline verified. No geometry refinements yet.'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
