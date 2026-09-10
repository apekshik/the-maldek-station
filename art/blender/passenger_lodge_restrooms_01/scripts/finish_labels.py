"""Idempotent correction for pre-final review copies; the main builder includes it."""
import bpy,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'));s=bpy.context.scene;s.frame_set(1)
for n in ['Women','Men']:
 o=bpy.data.objects['PLR_'+n+'_Entry_Sign']
 if o.data.align_x!='CENTER':
  o.data.align_x='CENTER';o.rotation_euler.z=math.pi;o.location.x+=.19
s.frame_set(40);s.render.filepath=str(P/'previews/03_women_interior.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'),compress=True)
