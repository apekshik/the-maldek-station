"""Editable control-door design study. Does not write to source buildings or Unreal."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1]
SOURCE=OUT.parent/'visual_fidelity_10/Maldek_Parking_Arrival.blend'
OUT.mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
def collection(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
leaf=collection('01_Moving_leaf');fixed=collection('02_Stationary_hardware');frame=collection('03_Review_frame');stage=collection('90_Studio');context=collection('91_Existing_control_building')
group=leaf
with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):
 b.materials=[n for n in a.materials if n.startswith('VF06_')]
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
blue=bpy.data.materials['VF06_Petrol_paint'];cream=bpy.data.materials['VF06_Warm_enamel'];steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized'];ochre=bpy.data.materials['VF06_Safety_ochre']
rubber=mat('D01_EPDM',(.009,.014,.013),0,.85);brushed=mat('D01_Brushed_stainless',(.43,.47,.46),.85,.32);dark=mat('D01_Recess',(.014,.021,.023),.3,.55);wear=mat('D01_Paint_edge_wear',(.24,.28,.27),.65,.65)
glass=mat('D01_Frosted_glass',(.79,.86,.83),0,.32)
gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=1.0;gp.inputs['IOR'].default_value=1.46
gn=glass.node_tree.nodes;gl=glass.node_tree.links
noise=gn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=420;noise.inputs['Detail'].default_value=2
tc=gn.new('ShaderNodeTexCoord');gl.new(tc.outputs['Object'],noise.inputs['Vector'])
bump=gn.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0003;gl.new(noise.outputs['Fac'],bump.inputs['Height']);gl.new(bump.outputs['Normal'],gp.inputs['Normal'])
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 group.objects.link(o);return o
def box(n,p,d,m,b=.0015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=link(bpy.context.object);o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=b;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,p,r,h,m,axis='Z',verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=h,location=p);o=link(bpy.context.object);o.name=n;o.data.materials.append(m)
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 mod=o.modifiers.new('Turned edge','BEVEL');mod.width=.0008;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def text(n,body,p,size,m,back=False):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.00015;o=bpy.data.objects.new(n,cu);group.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,math.pi if back else 0);cu.materials.append(m);return o
def screw(x,y,z):
 cyl('Countersunk_fastener',(x,y,z),.005,.002,brushed,'Y',16);box('Screw_slot',(x,y-.0013,z),(.006,.0005,.001),dark,.0002)
# Existing measured clear reveal: 1.300 m wide, 2.400 m high, threshold top 0.024 m.
# Leaf perimeter has a 6 mm reveal and a 10 mm gap above the existing threshold.
x0,x1=.006,1.294;z0,z1=.034,2.394
vl,vr,vb,vt=.14,1.16,1.34,2.22
# Cut the vision opening from continuous sheets to avoid artificial panel seams.
cut=box('Temporary_vision_tool',((vl+vr)/2,0,(vb+vt)/2),(vr-vl,.2,vt-vb),dark,0)
for n,y,depth,m in [('Leaf_slab',0,.045,blue),('Interior_enamel',.023,.001,cream)]:
 o=box(n,((x0+x1)/2,y,(z0+z1)/2),(x1-x0,depth,z1-z0),m,0)
 mod=o.modifiers.new('Through vision aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=o.modifiers.new('Continuous folded edge','BEVEL');mod.width=.0004;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
bpy.data.objects.remove(cut,do_unlink=True)
for y in [-.027,.028]:
 for x in [vl,vr]:box('Vision_bead_vertical',(x,y,(vb+vt)/2),(.024,.017,vt-vb+.026),steel)
 for z in [vb,vt]:box('Vision_bead_horizontal',((vl+vr)/2,y,z),(vr-vl-.024,.017,.024),steel)
box('Vision_glass',((vl+vr)/2,0,(vb+vt)/2),(vr-vl-.024,.008,vt-vb-.024),glass,.0006)
for x in [vl+.017,vr-.017]:box('Vision_gasket',(x,-.013,(vb+vt)/2),(.008,.015,vt-vb-.025),rubber)
for z in [vb+.017,vt-.017]:box('Vision_gasket',((vl+vr)/2,-.013,z),(vr-vl-.04,.015,.008),rubber)
# Replaceable protective lower plate, with actual fasteners and restrained scuffs.
for y in [-.0245,.0255]:
 box('Replaceable_kick_plate',(.65,y,.22),(1.17,.003,.31),brushed,.002)
 for x in [.085,.65,1.215]:
  for z in [.085,.355]:screw(x,y+(-.002 if y<0 else .002),z)
random.seed(28)
for i in range(24):
 x=random.uniform(.12,1.15);z=random.uniform(.10,.32);o=box('Boot_scuff',(x,-.0262,z),(random.uniform(.015,.10),.00025,.0007),dark,.0001);o.rotation_euler.y=random.uniform(-.22,.22)
# Face-mounted mechanical lock, levers both sides, latch tongue on leaf edge.
for side in [-1,1]:
 y=side*.028
 box('Lock_escutcheon',(1.15,y,1.06),(.068,.009,.25),brushed,.007)
 cyl('Lever_rosette',(1.15,side*.038,1.12),.023,.014,brushed,'Y')
 rod('Lever_spindle',(1.15,side*.04,1.12),(1.15,side*.089,1.12),.009,brushed)
 rod('Return_lever',(1.15,side*.089,1.12),(1.035,side*.089,1.12),.010,brushed)
 rod('Lever_return',(1.035,side*.089,1.12),(1.035,side*.062,1.12),.009,brushed)
 cyl('Lock_cylinder',(1.15,side*.035,1.0),.014,.010,brushed,'Y')
 box('Key_slot',(1.15,side*.041,1.0),(.002,.001,.014),dark)
 for z in [.965,1.17]:screw(1.15,side*.034,z)
box('Latch_edge_plate',(1.2945,0,1.08),(.003,.032,.18),brushed)
box('Latch_tongue',(1.300,0,1.10),(.013,.021,.027),brushed,.002)
box('Asset_number_plate',(.43,-.027,1.15),(.43,.006,.16),cream,.002)
text('Door_ID','C / 01',(.43,-.031,1.155),.066,steel)
text('Door_ID_sub','CONTROL',(.43,-.031,1.104),.021,steel)
for x in [.23,.63]:screw(x,-.031,1.15)
box('Instruction_plate',(.83,-.026,1.22),(.29,.004,.07),steel)
text('Pull_instruction','PULL TO OPEN',(.83,-.029,1.208),.025,cream)
# Small edge chips, explicitly local to handling and bottom corners.
for i in range(20):
 x=random.choice([.014,1.283]);z=random.uniform(.055,.75)
 box('Edge_chip',(x,-.0228,z),(.003,.0005,random.uniform(.003,.018)),wear,.0002)
# Alternating hinge knuckles: moving sections follow hinge empty, fixed ones stay.
for z in [.29,1.20,2.12]:
 group=leaf;box('Moving_hinge_strap',(.043,-.029,z),(.070,.009,.14),brushed)
 for dz in [-.06,0,.06]:cyl('Moving_hinge_knuckle',(.004,-.035,z+dz),.014,.029,brushed)
 for dz in [-.045,.045]:screw(.056,-.035,z+dz)
 group=fixed;box('Fixed_hinge_strap',(-.023,-.030,z),(.035,.008,.14),brushed)
 for dz in [-.030,.030]:cyl('Fixed_hinge_knuckle',(.004,-.035,z+dz),.014,.028,brushed)
 cyl('Hinge_pin',(.004,-.035,z),.005,.17,steel)
group=fixed
for x in [-.012,1.312]:box('Frame_stop',(x,.035,1.214),(.034,.020,2.36),steel)
box('Head_stop',(.65,.035,2.401),(1.29,.020,.026),steel)
for x in [.005,1.295]:box('EPDM_side_seal',(x,.025,1.214),(.009,.012,2.35),rubber,.002)
box('EPDM_head_seal',(.65,.025,2.389),(1.28,.012,.008),rubber,.002)
# Latch strike has a real slot, built as four pieces around its receiver.
for z in [1.03,1.17]:box('Strike_end',(1.309,0,z),(.017,.045,.050),brushed)
for y in [-.019,.019]:box('Strike_side',(1.309,y,1.10),(.017,.006,.09),brushed)
group=frame
for x in [-.035,1.335]:box('Review_jamb',(x,0,1.2),(.07,.28,2.4),steel)
box('Review_lintel',(.65,0,2.435),(1.44,.28,.07),steel)
box('Existing_threshold_proxy',(.65,0,.012),(1.3,.38,.024),zinc,.003)
box('Drip_cap',(.65,-.16,2.475),(1.48,.15,.018),zinc,.002)
group=leaf
pivot=bpy.data.objects.new('D01_HINGE_PIVOT',None);leaf.objects.link(pivot);pivot.location=(.004,-.035,0);pivot.empty_display_type='ARROWS';pivot.empty_display_size=.22
bpy.context.view_layer.update()
for o in list(leaf.objects):
 if o!=pivot:o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
for f,angle in [(1,0),(30,0),(90,-105),(120,-105)]:
 pivot.rotation_euler.z=math.radians(angle);pivot.keyframe_insert(data_path='rotation_euler',frame=f)
s.frame_end=120;s.frame_set(1)
# Read-only source building copy, positioned around the exact measured control doorway.
with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):b.collections=['VF06_Control']
src=b.collections[0]
T=Matrix.Translation(Vector((-2.65,0,-4)))@Matrix.Rotation(math.pi,4,'Z')
for o in list(src.objects):
 context.objects.link(o)
 o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
bpy.context.view_layer.update()
for o in list(src.objects):
 if o.parent is None:o.matrix_world=T@o.matrix_world
context.hide_render=True;context.hide_viewport=True
group=stage
floor=box('Studio_floor',(.65,0,-.055),(200,200,.08),mat('D01_Studio',(.075,.09,.09),0,.85),0)
def camera(n,p,target,lens=52):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
def area(n,p,target,power,color,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.color=color;d.shape='DISK';d.size=size
area('Key',(-2,-4,5),(.65,0,1),600,(1,.90,.76),4)
area('Fill',(4,-2,3),(.65,0,1.2),420,(.74,.87,1),3)
area('Rim',(1,3,4),(.65,0,1.5),650,(1,.95,.83),3)
cams=[camera('01_Closed', (3.0,-5.8,2.8),(.65,0,1.24),62),camera('02_Open', (3.7,-5.8,2.9),(.45,-.35,1.23),57),camera('03_Hardware',(2.08,-2.1,1.55),(1.05,0,1.10),72),camera('04_In_building',(3.4,-5.8,2.9),(-.10,0,1.35),42),camera('05_Interior',(-2.8,5.4,2.6),(.65,0,1.2),60)]
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.world.color=(.20,.20,.20);s.view_settings.view_transform='AgX';s.camera=cams[0]
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Control_Door_Study.blend'))
report={'source':str(SOURCE),'stage':'Blender design review; not game-ready','opening_m':[1.3,2.4],'leaf_m':[x1-x0,.045,z1-z0],'threshold_top_m':.024,'bottom_gap_m':z0-.024,'side_gap_m':.006,'hinge_local_m':list(pivot.location),'source_placement':{'rotation_z_degrees':180,'translation_m':[-2.65,0,4]},'frames':{'closed':1,'open_105_degrees':90},'materials':[m.name for m in bpy.data.materials if m.users],'pending':['Unreal material bake and UVs','Optimized moving mesh and collision','Per-opening swing/capsule validation','User design review before integration']}
(OUT/'design_manifest.json').write_text(json.dumps(report,indent=2))
for i,cam in enumerate(cams):
 s.camera=cam;s.frame_set(90 if i==1 else 1)
 context.hide_render=(i!=3);context.hide_viewport=(i!=3);frame.hide_render=(i==3)
 s.render.filepath=str(OUT/'previews'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
print('DOOR_STUDY_COMPLETE',flush=True)
