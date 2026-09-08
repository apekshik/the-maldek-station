"""Approved frosted door: standard and electronic keypad variants."""
import bpy,math,ast,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];OUT.mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
SOURCE=OUT.parent/'door_study_01/Maldek_Control_Door_Study.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1)
for n in ast.parse((OUT.parent/'door_study_01/scripts/build_door.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['mat','link','box','cyl','rod','text','screw','camera']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),'door_helpers','exec'))
stage=bpy.data.collections['90_Studio'];brushed=bpy.data.materials['D01_Brushed_stainless'];dark=bpy.data.materials['D01_Recess'];steel=bpy.data.materials['VF06_Structural_steel'];cream=bpy.data.materials['VF06_Warm_enamel']
rubber=bpy.data.materials['D01_EPDM'];case=mat('D03_Graphite_housing',(.035,.046,.048),.65,.36);keys=mat('D03_Keycaps',(.34,.38,.37),.75,.36)
screen=mat('D03_Display_lens',(.012,.032,.026),.1,.20);mark=mat('D03_Key_legends',(.68,.76,.65),.1,.44)
led=mat('D03_Status_red',(.32,.006,.002),0,.25);p=led.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.025,.005,1);p.inputs['Emission Strength'].default_value=.6
display=mat('D03_Display_text',(.40,.60,.46),0,.45);p=display.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.35,.60,.40,1);p.inputs['Emission Strength'].default_value=.3
def col(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
reader=col('04_Digital_keypad');inside=col('05_Interior_electronics');strike=col('06_Electronic_strike');group=reader
cx=.86
# Flush gasket, cast housing, inset stainless fascia and downward rain hood.
box('Reader_EPDM_back_gasket',(cx,-.026,1.045),(.146,.006,.264),rubber,.005)
box('Reader_cast_enclosure',(cx,-.048,1.045),(.142,.040,.260),case,.009)
box('Reader_stainless_fascia',(cx,-.070,1.041),(.124,.005,.237),brushed,.004)
box('Reader_dark_inset',(cx,-.0735,1.039),(.105,.003,.210),dark,.003)
box('Rain_hood_top',(cx,-.063,1.181),(.157,.079,.009),case,.003)
for x in [cx-.074,cx+.074]:box('Rain_hood_side',(x,-.062,1.16),(.007,.077,.039),case,.003)
box('Display_optical_bezel',(cx,-.076,1.122),(.099,.006,.034),case,.003)
box('Display_protective_lens',(cx,-.0795,1.122),(.087,.002,.023),screen,.001)
text('Display_LOCKED','LOCKED',(cx,-.081,1.119),.009,display)
text('Device_label','MALDEK / ACCESS',(cx,-.074,1.154),.0055,cream)
labels=['1','2','3','4','5','6','7','8','9','CLR','0','OK']
for i,label in enumerate(labels):
 x=cx+(i%3-1)*.033;z=1.077-(i//3)*.031
 box('Key_socket_'+label,(x,-.076,z),(.029,.006,.025),rubber,.002)
 box('Tactile_key_'+label,(x,-.081,z),(.025,.006,.021),keys,.003)
 text('Key_legend_'+label,label,(x,-.0846,z-.004),.010 if len(label)==1 else .0048,dark)
 # Protected gap exposes a real rim around every individual button.
 if label=='5':box('Tactile_locator',(x,-.085,z-.0075),(.006,.001,.001),brushed,.0004)
for x in [cx-.051,cx+.051]:
 for z in [.936,1.146]:
  cyl('Security_screw',(x,-.0745,z),.0026,.0018,brushed,'Y',16)
  # Recess and anti-tamper center pin.
  cyl('Security_screw_recess',(x,-.0756,z),.00125,.0004,dark,'Y',6)
  cyl('Security_screw_center_pin',(x,-.0759,z),.00035,.0004,brushed,'Y',12)
box('Status_indicator_bezel',(cx-.025,-.075,.954),(.023,.003,.008),case,.002)
box('Status_indicator_lens',(cx-.025,-.077,.954),(.016,.002,.004),led,.001)
text('Status_caption','SECURED',(cx+.017,-.076,.951),.0046,mark)
for x in [cx-.033,cx+.033]:
 box('Bottom_drain_slot',(x,-.06,.914),(.009,.013,.0015),dark,.0004)
group=inside
box('Interior_electronics_backplate',(cx,.028,1.045),(.148,.008,.264),rubber,.004)
box('Interior_battery_cover',(cx,.045,1.045),(.137,.028,.250),case,.006)
for z in [.94,1.15]:cyl('Interior_cover_screw',(cx,.060,z),.0028,.002,brushed,'Y',16)
box('Interior_cover_seam',(cx,.060,1.02),(.126,.001,.001),dark,.0003)
group=strike
box('Electronic_strike_housing',(1.324,.025,1.10),(.025,.068,.19),steel,.002)
box('Electric_keeper_face',(1.309,-.005,1.10),(.008,.015,.07),brushed,.001)
cyl('Keeper_pivot',(1.31,.002,1.10),.004,.08,brushed)
# Reader and battery cover move with the door. Wiring is concealed through the leaf.
bpy.context.view_layer.update();pivot=bpy.data.objects['D01_HINGE_PIVOT']
for c in [reader,inside]:
 for o in c.objects:o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
camera('07_Keypad_door',(3,-5.8,2.8),(.65,0,1.24),62)
camera('08_Keypad_detail',(1.10,-.67,1.23),(.86,-.055,1.052),72)
camera('09_Keypad_and_handle',(1.65,-1.8,1.63),(.92,0,1.17),78)
s.camera=bpy.data.objects['07_Keypad_door'];s.cycles.samples=64
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Digital_Door_Variants.blend'))
for name in ['07_Keypad_door','08_Keypad_detail','09_Keypad_and_handle','01_Closed']:
 for c in [reader,inside,strike]:c.hide_render=name=='01_Closed'
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
(OUT/'variant_manifest.json').write_text(json.dumps({'approved_base':str(SOURCE),'variants':['standard','digital_keypad'],'additional_keypad_collections':[reader.name,inside.name,strike.name],'key_layout':'3 x 4 tactile buttons: 0-9, CLR, OK','enclosure_mm':[142,40,260],'placement_status':'Choose secure-door locations only after review.'},indent=2))
