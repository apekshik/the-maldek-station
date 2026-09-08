"""Weathered single-lane central portal Maldek pylon. Blender 5, metres. Standalone editable study."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=bpy.data.collections.new('PYLON | export geometry');scene.collection.children.link(parts)
stage=bpy.data.collections.new('STUDY | staging - not exported');scene.collection.children.link(stage)
current=parts

def move(o,name,mat):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 current.objects.link(o)
 if mat:o.data.materials.append(mat)
 return o

def material(name,color,metal=0,rough=.45,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
paint=material('Pylon_Faded_Grey_Green',(.26,.31,.28),.12,.78)
dark=material('Pylon_Graphite',(.055,.07,.065),.35,.79)
galv=material('Pylon_Galvanized',(.27,.29,.265),.48,.72)
rubber=material('Pylon_Sheave_Liner',(.014,.019,.023),.1,.54)
concrete=material('Pylon_Concrete',(.28,.30,.28),0,.83)
red=material('Pylon_Marker_Red',(.7,.008,.004),.05,.25,8)
amber=material('Pylon_Safety_Amber',(.48,.30,.085),.06,.83)
white=material('Pylon_Lettering',(.83,.87,.85),.15,.45)
# Restrained large-scale concrete pores; no artificially heavy rust on new steel.
n=concrete.node_tree.nodes;l=concrete.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=14;tc=n.new('ShaderNodeTexCoord');l.new(tc.outputs['Object'],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.045;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])

def bevel(o,width=.03,segments=2):
 mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=width;mod.segments=segments
 mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return o

def box(name,p,d,mat,edge=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=move(bpy.context.object,name,mat);o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if edge:bevel(o,edge)
 return o

def tube(name,a,b,r1,r2=None,mat=paint,verts=48):
 a=Vector(a);b=Vector(b);delta=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r1 if r2 is None else r2,depth=delta.length,location=(a+b)/2)
 o=move(bpy.context.object,name,mat);o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def rod(name,a,b,r=.035,mat=galv):return tube(name,a,b,r,mat=mat,verts=12)
def text(name,body,p,size,mat,rotation=(math.pi/2,0,0)):
 bpy.ops.object.text_add(location=p,rotation=rotation);o=move(bpy.context.object,name,mat);o.data.body=body;o.data.size=size;o.data.align_x='CENTER';o.data.extrude=.002;o.data.space_character=1.13;return o

def flange(name,p,r,axis=Vector((0,0,1)),bolts=20):
 p=Vector(p);axis=Vector(axis).normalized();tube(name+'_ring',p-axis*.075,p+axis*.075,r,mat=galv)
 u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u).normalized()
 for k in range(bolts):
  q=p+(u*math.cos(k*math.tau/bolts)+v*math.sin(k*math.tau/bolts))*(r-.085)
  tube(name+'_bolt',q-axis*.11,q+axis*.13,.043,mat=dark,verts=6)

H=42.;shaft_top=43.55
# Each shaft has its own solid surface; rings intentionally conceal segment joins.
for side in [-1,1]:
 x0=side*4.6;x1=side*3.2
 box('Foundation_plinth', (x0,0,.4),(4.5,4.0,.8),concrete,.10)
 box('Raised_concrete_pedestal',(x0,0,1.0),(3.25,3.0,.4),concrete,.06)
 box('Base_plate',(x0,0,1.27),(2.85,2.7,.14),dark,.035)
 a=Vector((x0,0,1.34));b=Vector((x1,0,shaft_top));axis=(b-a).normalized()
 for k in range(4):
  t0=k/4;t1=(k+1)/4;q=a.lerp(b,t0);r=a.lerp(b,t1)
  tube('Tubular_leg_%s_section_%d'%(side,k+1),q,r,1.05-.34*t0,1.05-.34*t1)
  if k:flange('Leg_section_flange',q,1.20-.34*t0,axis)
 flange('Foundation_anchor_flange',a+axis*.11,1.30,axis,24)
 # Vertical base stiffener fins, sunk into shaft and kept off adjacent outer faces.
 for k in range(8):
  angle=k*math.tau/8;o=box('Anchor_gusset',(x0+1.02*math.cos(angle),1.02*math.sin(angle),1.7),(.44,.045,.65),galv,.008);o.rotation_euler.z=angle
 # Maintenance spine on rear surface, with continuous fall-arrest rail.
 for z in [1.6+i*.30 for i in range(144)]:
  t=(z-1.34)/(shaft_top-1.34);x=x0+(x1-x0)*t;rad=1.05-.34*t
  rod('Ladder_rung',(x-.23,rad+.22,z),(x+.23,rad+.22,z),.019)
 for dx in [-.26,.26]:rod('Ladder_stile',(x0+dx,1.28,1.55),(x1+dx,.92,44.6),.026)
 rod('Fall_arrest_rail',(x0,1.3,1.5),(x1,.94,43.65),.025,dark)
 # Separate front service hatch with a thick frame; no competing coplanar face.
 box('Electrical_enclosure_frame',(x0,-1.036,2.48),(.66,.10,1.1),dark,.055)
 box('Electrical_enclosure_cover',(x0,-1.102,2.48),(.54,.035,.97),galv,.04)
 rod('Enclosure_handle',(x0+.16,-1.147,2.4),(x0+.16,-1.147,2.59),.018,dark)
 box('Tower_identity_plate',(x0,-1.0,4.65),(.76,.09,.98),dark,.03)
 text('Tower_number','03',(x0,-1.06,4.37),.50,white)
 text('Tower_id','MLD / LINE A',(x0,-1.065,5.35),.13,white)
 # Thin amber maintenance identification band; not an emissive stripe.
 t0=(5.78-a.z)/(b.z-a.z);t1=(5.94-a.z)/(b.z-a.z)
 tube('Maintenance_band',a.lerp(b,t0),a.lerp(b,t1),1.05-.34*t0+.008,1.05-.34*t1+.008,amber)
# A central passenger lane passes THROUGH the open twin-leg portal.
# All transverse structure is above the rope. No beam crosses the cabin envelope.
box('Portal_overhead_girder',(0,0,44.05),(7.7,1.45,1.0),dark,.09)
box('Portal_top_flange',(0,0,44.59),(7.9,1.60,.08),galv,.025)
for side in [-1,1]:
 tube('Portal_knee_brace',(side*3.3,0,40.1),(side*1.95,0,43.55),.23,.20,paint)
 # Down-facing discrete inspection fixtures and head marker pods.
 box('Maintenance_light_housing',(side*2.45,-.76,43.82),(.45,.16,.16),dark,.035)
 tube('Beacon_base',(side*3.35,0,44.65),(side*3.35,0,44.81),.16,mat=dark)
 tube('Red_marker_lens',(side*3.35,0,44.81),(side*3.35,0,45.05),.12,mat=red)
# One central 12-sheave support assembly. Hanger clearance is reserved on +X side.
x=0.
for y in [-2.1,2.1]:
 box('Central_suspension_drop',(-.58,y,42.58),(.20,.24,2.14),dark,.035)
box('Head_longitudinal_carrier',(-.58,0,43.55),(.36,5.0,.28),galv,.035)
box('Main_rocker',(-.37,0,41.4),(.15,5.6,.34),galv,.04)
rod('Main_rocker_pin',(-.75,0,41.45),(-.32,0,41.45),.16,dark)
for center in [-2.1,2.1]:
 box('Secondary_rocker',(-.26,center,41.78),(.12,3.8,.21),galv,.03)
 for offset in [-1.60,-.96,-.32,.32,.96,1.60]:
  y=center+offset;z=42.02
  tube('Rubber_sheave',(-.075,y,z),(.075,y,z),.275,mat=rubber,verts=40)
  for dx in [-.097,.097]:
   tube('Sheave_side_disc',(dx-.017,y,z),(dx+.017,y,z),.293,mat=galv,verts=40)
   tube('Sheave_hub',(dx-.045,y,z),(dx+.045,y,z),.105,mat=dark,verts=24)
  rod('Sheave_axle',(-.35,y,z),(.17,y,z),.060,galv)
# Single side service deck, reached by the left shaft ladder.
cx=-1.50
for y in [-3.8+i*.20 for i in range(39)]:box('Walkway_grating',(cx,y,42.55),(.90,.045,.065),galv,.004)
for dx in [-.46,.46]:
 rod('Catwalk_stringer',(cx+dx,-3.9,42.44),(cx+dx,3.9,42.44),.048,dark)
 for y in [-3.85,-1.925,0,1.925,3.85]:rod('Guard_post',(cx+dx,y,42.55),(cx+dx,y,43.64),.025)
 for z in [43.08,43.64]:rod('Guard_rail',(cx+dx,-3.85,z),(cx+dx,3.85,z),.025)
for y in [-3.85,3.85]:
 for z in [43.08,43.64]:rod('Catwalk_end_guard',(cx-.46,y,z),(cx+.46,y,z),.025)
for y in [-2.9,2.9]:
 tube('Deck_hanger',(-1.5,y,42.40),(-1.5,y,43.52),.055,mat=dark)
for x in [-3.1+i*.13 for i in range(10)]:box('Ladder_transfer_grating',(x,1.18,42.55),(.04,.72,.065),galv,.004)
# Bare return-rope rollers ABOVE the head: no second cabin lane or hanger fittings.
for y in [-.95,-.32,.32,.95]:
 box('Return_roller_mount',(-2.35,y,44.72),(.42,.18,.18),dark,.02)
 tube('Return_rope_roller',(-2.46,y,44.90),(-2.24,y,44.90),.20,mat=rubber,verts=32)
 for dx in [-2.48,-2.22]:tube('Return_roller_flange',(dx-.012,y,44.90),(dx+.012,y,44.90),.22,mat=galv,verts=32)
for y in [-3.65,3.65]:
 box('Central_rope_sensor',(-.30,y,42.40),(.18,.19,.14),amber,.015)
# Finish weathering is evaluated in a shared world-coordinate frame, so it survives joining.
weather_origin=bpy.data.objects.new('Weathering_coordinate_frame',None);scene.collection.objects.link(weather_origin)
def weather(m,base,shade,metal,rough,amount):
 n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
 tc=n.new('ShaderNodeTexCoord');tc.object=weather_origin
 broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=1.25;broad.inputs['Detail'].default_value=4;l.new(tc.outputs['Object'],broad.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(*shade,1);ramp.color_ramp.elements[1].position=.77;ramp.color_ramp.elements[1].color=(*base,1);l.new(broad.outputs['Fac'],ramp.inputs[0])
 mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(13,13,.7);l.new(tc.outputs['Object'],mapping.inputs[0])
 streak=n.new('ShaderNodeTexNoise');streak.inputs['Scale'].default_value=1;streak.inputs['Detail'].default_value=3;l.new(mapping.outputs[0],streak.inputs['Vector'])
 mask=n.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.60;mask.color_ramp.elements[1].position=.76;mask.color_ramp.elements[1].color=(amount,amount,amount,1);l.new(streak.outputs['Fac'],mask.inputs[0])
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.17,.065,.022,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Base Color'])
 bs.inputs['Metallic'].default_value=metal
 rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=rough;rr.inputs['To Max'].default_value=.94;l.new(broad.outputs['Fac'],rr.inputs['Value']);l.new(rr.outputs[0],bs.inputs['Roughness'])
 fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=35;fine.inputs['Detail'].default_value=2;l.new(tc.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.007;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
weather(paint,(.30,.34,.30),(.13,.17,.145),.10,.74,.55)
weather(dark,(.095,.115,.10),(.028,.039,.032),.22,.76,.65)
weather(galv,(.40,.42,.37),(.13,.16,.14),.40,.68,.7)
weather(amber,(.54,.35,.095),(.25,.18,.07),.03,.8,.35)
# Dedicated collar patina concentrates corrosion at joints rather than coating whole shafts.
rust=material('Pylon_Joint_Patina',(.19,.072,.021),.1,.91);weather(rust,(.24,.095,.032),(.06,.035,.018),.1,.86,.3)
for o in list(parts.objects):
 if any(t in o.name for t in ['flange_ring','flange_bolt','Anchor_gusset']):
  o.data.materials.clear();o.data.materials.append(rust)
# Export specification. Separate editable original and consolidated export copies.
scene['Design']='Maldek single central passenger lane / overhead portal / weathered finish'
scene['Reference']='https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/'
scene['Route_placement']='Pending actual Unreal terrain and cable alignment. Studio cable samples are NOT exported.'
# Studio cable samples and human scale figure.
current=stage
rod('STUDY_central_passenger_rope',(0,-32,42.327),(0,32,42.327),.032,dark)
rod('STUDY_bare_return_rope',(-2.35,-32,45.132),(-2.35,32,45.132),.032,dark)
figure=material('STUDY_Scale_Figure',(.11,.17,.19),.05,.5)
for x in [0]:
 tube('STUDY_human_torso',(x,-3.2,.88),(x,-3.2,1.45),.19,.25,figure)
 rod('STUDY_human_neck',(x,-3.2,1.44),(x,-3.2,1.60),.065,figure)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.13,location=(x,-3.2,1.68));move(bpy.context.object,'STUDY_human_head',figure)
 for s in [-1,1]:
  box('STUDY_human_boot',(x+s*.16,-3.25,.07),(.18,.30,.14),figure,.035)
  rod('STUDY_human_leg',(x+s*.12,-3.2,.9),(x+s*.16,-3.2,.12),.085,figure)
  rod('STUDY_human_arm',(x+s*.23,-3.2,1.40),(x+s*.33,-3.2,.91),.06,figure)
groundmat=material('STUDY_Ground',(.13,.155,.16),.05,.7)
box('STUDY_ground',(0,0,-.13),(2000,2000,.25),groundmat,.0)
# The approved cabin is a study-only reference; no production cabin asset is changed.
source=OUT.parents[2]/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.collections=['12_Gondola','VF06_Gondola_Details']
for c in loaded.collections:stage.children.link(c)
bpy.context.view_layer.update()
cabin_objects=[];transforms={}
for c in loaded.collections:
 for ob in c.all_objects:
  if ob not in cabin_objects and ob.type in {'MESH','CURVE','FONT'}:cabin_objects.append(ob);transforms[ob]=ob.matrix_world.copy()
for ob in cabin_objects:
 ob.parent=None;ob.matrix_world=transforms[ob];ob.location+=Vector((.10,-15.05,33.45));ob.name='STUDY_CABIN_'+ob.name
# A small side-clearing upper hanger is a concept adapter; kept out of the tower FBX.
adapter=[]
for a,b in [((.1,-7,41.36),(.72,-7,41.36)),((.72,-7,41.36),(.72,-7,42.49)),((.72,-7,42.49),(.04,-7,42.49)),((.04,-7,42.49),(.04,-7,42.327))]:
 adapter.append(tube('STUDY_CABIN_hanger_adapter',a,b,.060,mat=dark,verts=16))
cabin_objects+=adapter
scene['Cabin_adapter']='Study-only side-clearing upper hanger, existing cabin body retained; production rig unchanged.'

# Lighting and cameras deliberately independent of the production level.
world=bpy.data.worlds.new('Studio cool sky');scene.world=world;world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.32,.40,.48,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.55

def area(name,p,target,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Key_softbox',(-24,-25,50),(0,0,26),16000,(.80,.89,1),24)
area('Warm_edge',(17,12,36),(0,0,25),21000,(1,.79,.59),18)
area('Front_fill',(15,-18,27),(0,0,22),6500,(.65,.8,1),15)
sun=bpy.data.lights.new('Daylight','SUN');sun.energy=2;sun.angle=.14;o=bpy.data.objects.new('Daylight',sun);stage.objects.link(o);o.rotation_euler=(.40,-.55,-.6)

def camera(name,p,target,lens):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=3000;return o
cams={
 '01_full_pylon':camera('CAM_01_Full',(62,-91,39),(0,0,22),57),
 '02_crosshead':camera('CAM_02_Crosshead',(15,-23,46),(0,0,42),57),
 '03_base_detail':camera('CAM_03_Base',(10,-16,6),(1,0,3.1),55),
 '04_front_clearance':camera('CAM_04_Front',(0,-29,40.8),(0,0,40.8),55),
 '05_hanger_detail':camera('CAM_05_Hanger',(4,-12,43),(0,-7,41.9),62),
 '06_night':camera('CAM_04_Night',(57,-87,36),(0,0,22),55)}
scene.camera=cams['01_full_pylon'];scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 scene.cycles.device='GPU'
except Exception:pass
scene.render.resolution_x=1500;scene.render.resolution_y=1700;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.5
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
# Editable scene includes named parts; geometry only exported with evaluated bevels.
bpy.context.view_layer.update();objects=[o for o in parts.objects if o.type in {'MESH','FONT'}]
report={'design_height_m':45.12,'rope_height_m':42.327,'base_leg_spacing_m':9.2,'passenger_lanes':1,'passenger_rope_x_m':0,'bare_return_rope_x_m':-2.35,'shaft_diameter_base_m':2.1,'shaft_diameter_top_m':1.42,'sheaves_per_lane':12,'objects':len(objects),'route_status':'standalone study - not imported','sources':[{'url':'https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/','used':'Modular circular tubes, special twin legs, flange joints, sheave trains and catwalks'},{'url':'https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR199_ENG.pdf','used':'550 mm sheave diameter as detail proportion reference'}]}
# Basic evaluated mesh sanity and persistent metric metadata.
deps=bpy.context.evaluated_depsgraph_get();invalid=[];triangles=0
for o in objects:
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles)
 if any(not math.isfinite(c) for v in me.vertices for c in v.co):invalid.append(o.name)
 ev.to_mesh_clear()
assert not invalid;report['evaluated_triangles']=triangles
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Weathered_Central_Pylon.blend'))
# Consolidation by material for UE: one reusable asset, kept separate from authoring scene.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.duplicate();copies=list(bpy.context.selected_objects);bpy.ops.object.convert(target='MESH');bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SM_Maldek_Central_Pylon';scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'fbx/SM_Maldek_Central_Pylon.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
bpy.data.objects.remove(mesh,do_unlink=True)
for name,cam in cams.items():
 scene.camera=cam
 if name=='04_front_clearance':
  for ob in cabin_objects:ob.location.y+=7
 if name=='06_night':
  sun.energy=.035;world.node_tree.nodes.get('Background').inputs[1].default_value=.025
  for ob in stage.objects:
   if ob.type=='LIGHT' and ob.data.type=='AREA':ob.data.energy*=.12
  scene.view_settings.exposure=.3
 if name=='02_crosshead':scene.render.resolution_x=1800;scene.render.resolution_y=1200
 elif name in ['03_base_detail','04_front_clearance','05_hanger_detail']:scene.render.resolution_x=1500;scene.render.resolution_y=1100
 else:scene.render.resolution_x=1500;scene.render.resolution_y=1700
 scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
 if name=='04_front_clearance':
  for ob in cabin_objects:ob.location.y-=7
print('CENTRAL_PYLON_STUDY_COMPLETE',json.dumps(report))
