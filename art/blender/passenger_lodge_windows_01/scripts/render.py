"""Render the saved fitted package. Optional camera names after --."""
import bpy,json,sys,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Windows.blend'))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [o.name for o in bpy.data.collections['PLW_REVIEW_ONLY__DO_NOT_EXPORT'].objects if o.type=='CAMERA']
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
records=json.loads((OUT/'review_views.json').read_text()) if (OUT/'review_views.json').exists() else []
for name in names:
    s.camera=bpy.data.objects[name]
    for o in bpy.data.collections['PLW_REVIEW_ONLY__DO_NOT_EXPORT'].objects:
        if o.type=='LIGHT':o.hide_render='Facade' in name
    # Roof hidden only for geometry inspection, kept on for all fitted renders.
    bpy.data.collections['PL03_Removable_Roof'].hide_render=False
    s.render.filepath=str(OUT/'previews'/f'{name}.png')
    bpy.ops.render.render(write_still=True,scene=s.name)
    records=[r for r in records if r['image']!=name+'.png']
    records.append(dict(image=name+'.png',position_m=list(s.camera.location),lens_mm=s.camera.data.lens,roof_visible=True,lighting='Unchanged source lighting' if 'Facade' in name else 'Source world plus labelled neutral temporary softboxes'))
(OUT/'review_views.json').write_text(json.dumps(records,indent=2))
