"""Export a relay-labelled leaf from the approved digital source; geometry/pivot unchanged."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/doors';sys.path.insert(0,str(out.parent/'scripts'));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/door_study_03/Maldek_Digital_Door_Variants.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));bpy.context.scene.frame_set(1)
assert bpy.data.objects['Door_ID'].data.body=='C / 01';bpy.data.objects['Door_ID'].data.body='R / 01';bpy.data.objects['Door_ID_sub'].data.body='RELAY'
c=bpy.data.collections['01_Moving_leaf'];c.hide_render=False;c.hide_viewport=False
objects=[o for o in c.objects if o.name!='Vision_glass']
for o in objects:o.hide_render=False
bpy.context.view_layer.update();handoff=h.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx');row=handoff.chunk('SM_StationDoor_RelayLeaf',objects,pivot=(.004,-.035,0),role='thin')
(out/'relay_leaf_manifest.json').write_text(json.dumps({'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'edits':{'Door_ID':'R / 01','Door_ID_sub':'RELAY'},'chunks':[row]},indent=2))
