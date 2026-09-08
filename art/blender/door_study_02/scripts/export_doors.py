import bpy,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'art/unreal_handoff/revision12/doors';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(OUT.parent/'scripts'));import mesh_handoff as h
h.OUT=OUT;h.SOURCE=ROOT/'art/blender/door_study_03/Maldek_Digital_Door_Variants.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));s=bpy.context.scene;s.frame_set(1)
groups={'Leaf':('01_Moving_leaf',lambda o:o.name!='Vision_glass'),'Glass':('01_Moving_leaf',lambda o:o.name=='Vision_glass'),'Fixed':('02_Stationary_hardware',lambda o:True),'Keypad':('04_Digital_keypad',lambda o:True),'InteriorElectronics':('05_Interior_electronics',lambda o:True),'ElectronicStrike':('06_Electronic_strike',lambda o:True)}
for cn,_ in groups.values():
 c=bpy.data.collections[cn];c.hide_render=False;c.hide_viewport=False
bpy.context.view_layer.update();handoff=h.Handoff(s,bpy.context.evaluated_depsgraph_get(),'fbx')
for name,(cn,pred) in groups.items():
 objects=[o for o in bpy.data.collections[cn].objects if pred(o)]
 for o in objects:o.hide_render=False
 handoff.chunk('SM_StationDoor_'+name,objects,pivot=(.004,-.035,0),role='glass' if name=='Glass' else 'thin')
handoff.save('door_manifest')
