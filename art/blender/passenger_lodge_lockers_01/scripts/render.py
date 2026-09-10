"""Render saved fitted package using explicitly temporary neutral review lighting."""
import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'))
s=bpy.context.scene
# Prefer available compute device; CPU fallback remains reproducible.
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type!='CPU'
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
(OUT/'previews').mkdir(exist_ok=True)
for v in json.loads((OUT/'replacement_manifest.json').read_text())['views']:
 s.frame_set(v['frame']);s.camera=bpy.data.objects['REVIEW_'+v['name']]
 bpy.data.collections['REFERENCE_ONLY_Source_Context'].hide_render=v['name']=='rear_attachment'
 s.render.filepath=str(OUT/'previews'/ (v['name']+'.png'));bpy.ops.render.render(write_still=True)
print('REVIEW COMPLETE')
