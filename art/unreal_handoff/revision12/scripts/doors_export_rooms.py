import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/doors';sys.path.insert(0,str(out.parent/'scripts'));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/door_study_03/Maldek_Digital_Door_Variants.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));bpy.context.scene.frame_set(1)
c=bpy.data.collections['01_Moving_leaf'];c.hide_render=False;c.hide_viewport=False;objects=[o for o in c.objects if o.name!='Vision_glass']
for o in objects:o.hide_render=False
handoff=h.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx')
for name,code,label in [('Quarters','Q / 01','QUARTERS'),('Hall','H / 01','WAITING HALL'),('Generator','G / 01','GENERATOR'),('Workshop','W / 01','WORKSHOP')]:
 bpy.data.objects['Door_ID'].data.body=code;bpy.data.objects['Door_ID_sub'].data.body=label;bpy.context.view_layer.update();handoff.deps=bpy.context.evaluated_depsgraph_get();handoff.chunk('SM_StationDoor_'+name+'Leaf',objects,pivot=(.004,-.035,0),role='thin')
(out/'room_leaf_manifest.json').write_text(json.dumps({'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'chunks':handoff.chunks},indent=2))
