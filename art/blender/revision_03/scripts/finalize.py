import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
notes=bpy.data.texts.get('START_HERE');notes.clear();notes.write('MILLFORD / MALDEK NIGHT STUDY 03\n\nContinuous relay paths and filled eastern shoulder. Relay now at (48,13,3) metres. Textured CC0 Poly Haven pine variants. Cable route to distant Maldek. Night lighting, wet surfaces, layered fog and static rain.\n\nFull Shell for rendering; Cutaway and Lower Level for editing. See revision_03/README.md and validation_report.json. No new UE export or engine playtest in this revision. Earlier files preserved.\n')
scene['Status']='Revision03 geometry samples passed; new relay paths, pine assets, cable route and night rain study. UE5 validation pending.'
scene.camera=bpy.data.objects['CAM_R03_Platform_Rain']
# Start in an overview suitable for navigating the enlarged site, preserving night render settings.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(15,8,3);sp.region_3d.view_distance=90;sp.region_3d.view_rotation=bpy.data.objects['CAM_R03_Relay_Terrain'].rotation_euler.to_quaternion();sp.region_3d.view_perspective='PERSP'
assert scene.view_settings.exposure<0
assert not bpy.data.objects['Valley_Fog_Volume'].hide_render
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_night_03.blend'))
print('FINALIZED_NIGHT_SCENE',flush=True)
