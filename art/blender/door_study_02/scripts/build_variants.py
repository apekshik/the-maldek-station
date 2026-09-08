import bpy,math,ast,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];OUT.mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
SOURCE=OUT.parent/'door_study_01/Maldek_Control_Door_Study.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1)
for n in ast.parse((OUT.parent/'door_study_01/scripts/build_door.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['mat','link','box','cyl','rod','text','screw','camera']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),'door_helpers','exec'))
stage=bpy.data.collections['90_Studio'];brushed=bpy.data.materials['D01_Brushed_stainless'];dark=bpy.data.materials['D01_Recess'];steel=bpy.data.materials['VF06_Structural_steel']
brass=mat('D02_Aged_brass',(.40,.245,.075),.82,.32);chrome=mat('D02_Hardened_shackle',(.38,.43,.44),.95,.24);black=mat('D02_Lock_recess',(.013,.011,.007),.2,.7)
n=brass.node_tree.nodes;l=brass.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=160;noise.inputs['Detail'].default_value=3
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0001;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
def col(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
hasp=col('04_Hasp_moving');staple=col('05_Hasp_fixed');padlock=col('06_Padlock_removable')
# Right latch edge: the door skin sits 0.12 m behind the existing frame face.
# Solid spacer and backed hinge mounting align the hasp with that frame face.
group=hasp
box('Hasp_spacer',(1.195,-.085,.90),(.065,.12,.095),steel,.004)
box('Hasp_hinge_mount',(1.195,-.151,.90),(.076,.012,.102),brushed,.002)
for x in [1.172,1.218]:
 for z in [.868,.932]:screw(x,-.158,z)
# Hinge barrel vertical; flap may be swung off the staple after padlock removal.
cyl('Hasp_hinge_pin',(1.228,-.164,.90),.005,.072,chrome)
for dz in [-.024,0,.024]:cyl('Hasp_hinge_barrel',(1.228,-.164,.90+dz),.009,.022,brushed)
flap=box('Hasp_slotted_flap',(1.287,-.175,.90),(.118,.009,.049),brushed,.003)
tool=box('TEMP_staple_slot',(1.329,-.175,.90),(.013,.05,.029),black,0)
mod=flap.modifiers.new('Actual staple opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=tool
bpy.context.view_layer.objects.active=flap;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
group=staple
box('Staple_backing_plate',(1.335,-.148,.90),(.054,.012,.100),brushed,.003)
for z in [.865,.935]:screw(1.335,-.155,z)
# Vertical staple loop projects through flap; loop lies in the YZ plane.
cu=bpy.data.curves.new('Staple_closed_loop','CURVE');cu.dimensions='3D';cu.bevel_depth=.004;cu.bevel_resolution=4;sp=cu.splines.new('POLY');pts=[]
for i in range(49):
 t=2*math.pi*i/48;pts.append((1.329,-.174-.017*math.cos(t),.90+.010*math.sin(t)))
sp.points.add(len(pts)-1)
for q,p in zip(sp.points,pts):q.co=(*p,1)
o=bpy.data.objects.new('Staple_loop',cu);group.objects.link(o);cu.materials.append(chrome)
group=padlock
cx=1.329;cy=-.184;cz=.816
body=box('Padlock_forged_body',(cx,cy,cz),(.060,.028,.058),brass,.004)
box('Padlock_lower_retainer',(cx,cy,cz-.027),(.052,.025,.006),brass,.002)
# U-shaped shackle with parallel legs and a smoothly swept semicircle.
cu=bpy.data.curves.new('Padlock_U_shackle','CURVE');cu.dimensions='3D';cu.bevel_depth=.0045;cu.bevel_resolution=5
pts=[(cx-.019,cy,.839),(cx-.019,cy,.881)]
for i in range(33):
 a=math.pi-math.pi*i/32;pts.append((cx+.019*math.cos(a),cy,.881+.019*math.sin(a)))
pts.extend([(cx+.019,cy,.857),(cx+.019,cy,.839)])
sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
for q,p in zip(sp.points,pts):q.co=(*p,1)
o=bpy.data.objects.new('Padlock_hardened_U_shackle',cu);group.objects.link(o);cu.materials.append(chrome)
for x in [cx-.019,cx+.019]:
 cyl('Shackle_socket_seal',(x,cy,.845),.0065,.002,black)
 cyl('Shackle_socket_ring',(x,cy,.8465),.0058,.0015,brass)
# Face plate, stamp, shallow grooves and retained pins.
box('Padlock_face_inset',(cx,cy-.0146,cz),(.043,.0015,.035),brass,.002)
text('Lock_brand','M / S',(cx,cy-.0156,cz+.004),.007,black)
text('Lock_grade','HARDENED',(cx,cy-.0156,cz-.006),.0032,black)
text('Lock_serial','024 - 06',(cx,cy-.0156,cz-.013),.0028,black)
for x in [cx-.024,cx+.024]:
 cyl('Body_retainer_pin',(x,cy-.0145,cz-.018),.0015,.001,chrome,'Y',16)
for z in [cz-.021,cz+.021]:box('Machined_body_line',(cx,cy-.0144,z),(.046,.0004,.00055),black,.0001)
# Cylinder and paracentric keyway on the underside, visible in macro camera.
cyl('Underside_key_cylinder',(cx,cy,cz-.031),.009,.003,chrome)
box('Keyway_vertical',(cx,cy,cz-.0327),(.0018,.011,.0007),black,.0001)
box('Keyway_ward',(cx+.0014,cy+.001,cz-.0328),(.004,.0017,.0007),black,.0001)
cyl('Drain_hole',(cx+.021,cy,cz-.0297),.0015,.0006,black)
for i in range(9):
 o=box('Brass_handling_scratch',(cx-.021+i*.005,cy-.0149,cz+.015-(i%3)*.003),(.004,.0002,.0002),chrome,.00005);o.rotation_euler.y=.3
# Hasp follows the leaf; padlock and staple are fixed while secured.
bpy.context.view_layer.update();pivot=bpy.data.objects['D01_HINGE_PIVOT']
for o in hasp.objects:o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
camera('07_Padlocked_door',(3,-5.8,2.8),(.65,0,1.24),62)
camera('08_Padlock_detail',(1.49,-.52,.78),(1.29,-.17,.865),65)
camera('09_Padlock_underside',(1.42,-.40,.68),(1.329,-.20,.827),70)
# Two reusable collections, kept at matching coordinates. Visibility is the variant switch.
s.camera=bpy.data.objects['07_Padlocked_door'];s.cycles.samples=64
for c in [hasp,staple,padlock]:c.hide_render=False;c.hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Door_Variants.blend'))
for name in ['07_Padlocked_door','08_Padlock_detail','09_Padlock_underside','01_Closed']:
 for c in [hasp,staple,padlock]:c.hide_render=name=='01_Closed'
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
(OUT/'variant_manifest.json').write_text(json.dumps({'approved_base':str(SOURCE),'variants':{'standard':{'collections':['01_Moving_leaf','02_Stationary_hardware']},'padlocked':{'additional_collections':[hasp.name,staple.name,padlock.name]}},'padlock_body_mm':[60,28,58],'shackle_diameter_mm':9,'placement_status':'User requested choosing lock locations after reviewing variants.'},indent=2))
