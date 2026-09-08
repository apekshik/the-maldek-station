"""Export the completed cabin with independent sliding/rotating parts and explicit cabin collision."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/gondola_cabin';out.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(__file__).parent));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/gondola_cabin_01/Maldek_Gondola_Cabin.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));s=bpy.context.scene;s.frame_set(60);bpy.context.view_layer.update()
# Explicit collision avoids filling windows/entrance with an assembly-wide hull.
h.collision_kind=lambda o:None
handoff=h.Handoff(s,bpy.context.evaluated_depsgraph_get(),'fbx')
def box(center,size,name):
 return {'min':[center[i]-size[i]/2 for i in range(3)],'max':[center[i]+size[i]/2 for i in range(3)],'source':name,'kind':'authored'}
boxes=[box((0,0,-.06),(3.10,6,.12),'cabin floor'),box((0,2.98,1.15),(3.10,.10,2.30),'rear enclosure'),box((0,0,2.34),(3.1,6,.10),'roof'),box((0,-3.02,2.20),(3.1,.12,.20),'entry head')]
for sign in [-1,1]:
 boxes.extend([box((sign*1.50,0,1.15),(.10,6,2.3),'side enclosure'),box((sign*1.06,-3.02,1.05),(.92,.12,2.1),'entry jamb'),box((sign*1.25,0,.25),(.50,4.60,.50),'bench')])
pinion=bpy.data.objects['GC_DRIVE_PINION'];rollers=sorted([o for o in s.objects if o.name.startswith('GC_ROLLER')],key=lambda o:o.name)
rotating=set(pinion.children)
for o in rollers:rotating.update(o.children)
leaves=[]
for side in ['Left','Right']:
 c=bpy.data.collections['02_Left_sliding_leaf' if side=='Left' else '03_Right_sliding_leaf']
 obs=[o for o in c.objects if o not in rotating];leaves.extend(c.objects)
 handoff.chunk('SM_Gondola_Door'+side,obs,role='thin')
handoff.chunk('SM_Gondola_Pinion',list(pinion.children),pivot=pinion.matrix_world.translation,role='thin')
handoff.chunk('SM_Gondola_Roller',list(rollers[0].children),pivot=rollers[0].matrix_world.translation,role='thin')
fixed=[]
for name in ['12_Gondola','VF06_Gondola_Details','01_Door_fixed_track_and_drive','04_Cabin_interior_details']:
 fixed.extend(o for o in bpy.data.collections[name].all_objects if o not in rotating and o not in leaves and o.type in {'MESH','CURVE','FONT'})
fixed=list(set(fixed))
def glass(o):return any(m and ('glass' in m.name.lower()) for m in o.data.materials)
handoff.chunk('SM_Gondola_CabinShell',[o for o in fixed if not glass(o)],extra_boxes=boxes,role='thin')
handoff.chunk('SM_Gondola_CabinGlass',[o for o in fixed if glass(o)],role='glass')
manifest={'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'materials':handoff.materials,'chunks':handoff.chunks,'units':'metres converted once to cm','placement':'Imported (x,-y,z), yaw 180 produces cabin (-x,y,z); origin at floor centre.','door_travel_cm':63.5,'structural_opening_cm':[120,210],'review_lights_exported':False}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('CABIN_EXPORT_COMPLETE',len(handoff.chunks))
