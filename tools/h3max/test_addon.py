"""Blender smoke test: register, preset roundtrip and isolated guide capture; no API."""
import bpy,addon_utils,sys,json,time
from pathlib import Path
addon_utils.enable('maldek_h3',default_set=False)
import maldek_h3 as addon
p=bpy.context.scene.maldek_h3
original_file=bpy.data.filepath
p.darkness=.91;p.fog=.88
p.preset_name='smoke-test'
assert bpy.ops.maldek_h3.preset(load=False)=={'FINISHED'}
p.fog=.1
assert bpy.ops.maldek_h3.preset(load=True)=={'FINISHED'}
assert abs(p.fog-.88)<.001
p.mode='STILL';p.guide='LINES'
bpy.context.scene.camera=bpy.data.objects['CAM_R03_Platform_Rain']
layer=bpy.context.scene.view_layers.get('02_Full_Shell')
if layer:bpy.context.window.view_layer=layer
assert bpy.ops.maldek_h3.run(generate=False)=={'FINISHED'}
assert bpy.data.filepath==original_file,'Source path changed'
deadline=time.monotonic()+100
while addon._job and time.monotonic()<deadline:
    addon.tick();time.sleep(.2)
assert addon._job is None,'Worker did not finish'
assert p.history and Path(p.history[-1].path).exists(),p.status
assert not (Path(p.history[-1].path).parent/'api').exists(),'Unexpected API job'
print('ADDON_SMOKE_OK',p.history[-1].path)
