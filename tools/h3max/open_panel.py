"""Open an isolated look-development workspace, leaving modeling windows alone."""
import bpy,addon_utils
from pathlib import Path
addon_utils.enable('maldek_h3',default_set=False)
base=Path(__file__).resolve().parents[2]
s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=720
s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1
s.camera=bpy.data.objects['CAM_R03_Platform_Rain']
bpy.context.window.view_layer=s.view_layers['02_Full_Shell']
p=s.maldek_h3
for folder,title in [('refined-exterior-realism-03','Photographic exterior'),('refined-exterior-dark-fog-04','Dark fog exterior')]:
    path=base/'art/blender/h3max/outputs'/folder/'h3_review.mp4'
    if path.exists():
        item=p.history.add();item.name=title;item.path=str(path)
p.selected=max(0,len(p.history)-1)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.show_region_ui=True;sp.region_3d.view_perspective='CAMERA'
        sp.shading.type='MATERIAL'
bpy.context.workspace.name='H3 Look Development'
out=base/'art/blender/h3max/outputs/Maldek_H3_Workspace.blend'
if not out.exists():bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('H3_WORKSPACE_READY',flush=True)
