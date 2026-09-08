"""Modern twin-tube Maldek pylon. Blender 5, metres. Standalone editable study."""
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
paint=material('Pylon_Satin_Silver',(.47,.56,.59),.45,.44)
dark=material('Pylon_Graphite',(.045,.065,.073),.72,.33)
galv=material('Pylon_Galvanized',(.38,.43,.45),.85,.28)
rubber=material('Pylon_Sheave_Liner',(.014,.019,.023),.1,.54)
concrete=material('Pylon_Concrete',(.28,.30,.28),0,.83)
red=material('Pylon_Marker_Red',(.7,.008,.004),.05,.25,8)
amber=material('Pylon_Safety_Amber',(.88,.40,.06),.25,.37)
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

H=42.;shaft_top=40.6
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
 for z in [1.6+i*.30 for i in range(134)]:
  t=(z-1.34)/(shaft_top-1.34);x=x0+(x1-x0)*t;rad=1.05-.34*t
  rod('Ladder_rung',(x-.23,rad+.22,z),(x+.23,rad+.22,z),.019)
 for dx in [-.26,.26]:rod('Ladder_stile',(x0+dx,1.28,1.55),(x1+dx,.92,42.6),.026)
 rod('Fall_arrest_rail',(x0,1.3,1.5),(x1,.94,41.65),.025,dark)
 # Separate front service hatch with a thick frame; no competing coplanar face.
 box('Electrical_enclosure_frame',(x0,-1.036,2.48),(.66,.10,1.1),dark,.055)
 box('Electrical_enclosure_cover',(x0,-1.102,2.48),(.54,.035,.97),galv,.04)
 rod('Enclosure_handle',(x0+.16,-1.147,2.4),(x0+.16,-1.147,2.59),.018,dark)
 box('Tower_identity_plate',(x0,-1.0,4.65),(.76,.09,.98),dark,.03)
 text('Tower_number','03',(x0,-1.06,4.37),.50,white)
 text('Tower_id','MLD / LINE A',(x0,-1.065,5.35),.13,white)
 # Thin amber maintenance identification band; not an emissive stripe.
 tube('Maintenance_band',(x0+(x1-x0)*.115,0,5.78),(x0+(x1-x0)*.119,0,5.94),1.018,1.017,amber)
# Transverse tube brace lower than the cabin passage. Quiet silhouette, no lattice.
tube('Upper_transverse_tie',(-3.48,0,32.9),(3.48,0,32.9),.36,mat=dark)
for side in [-1,1]:tube('Shoulder_tube', (side*3.34,0,36.4),(side*5.3,0,40.8),.34,.29,paint)
box('Crosshead_box_girder',(0,0,41.05),(12.5,1.3,.90),dark,.11)
box('Crosshead_top_flange',(0,0,41.54),(12.7,1.48,.08),galv,.025)
# Two longitudinal 12-sheave rocker trains, mounted at the crosshead ends.
for side in [-1,1]:
 x=side*7.1
 box('Cantilever_mount',(side*6.36,0,41.1),(1.1,.8,.48),galv,.04)
 rod('Main_rocker_pin',(x-side*.92,0,41.25),(x-side*.25,0,41.25),.19,dark)
 box('Main_rocker',(x-side*.37,0,41.4),(.15,5.6,.34),galv,.05)
 for center in [-2.1,2.1]:
  box('Secondary_rocker',(x-side*.26,center,41.78),(.12,3.28,.21),galv,.03)
  for offset in [-1.60,-.96,-.32,.32,.96,1.60]:
   y=center+offset;z=42.02
   # Inset hub, rubber groove, proud flange on both faces, distinct surfaces.
   tube('Rubber_sheave', (x-.075,y,z),(x+.075,y,z),.275,mat=rubber,verts=40)
   for dx in [-.097,.097]:
    tube('Sheave_side_disc',(x+dx-.017,y,z),(x+dx+.017,y,z),.293,mat=galv,verts=40)
    tube('Sheave_hub',(x+dx-.045,y,z),(x+dx+.045,y,z),.105,mat=dark,verts=24)
   rod('Sheave_axle',(x-side*.35,y,z),(x+side*.17,y,z),.060,galv)
 # Inboard service catwalks do not cover the rope or the sheave groove.
 cx=x-side*1.0
 for y in [-3.8+i*.20 for i in range(39)]:box('Walkway_grating',(cx,y,42.15),(.78,.045,.065),galv,.004)
 for dx in [-.4,.4]:
  rod('Catwalk_stringer',(cx+dx,-3.9,42.06),(cx+dx,3.9,42.06),.048,dark)
  for y in [-3.85,-1.925,0,1.925,3.85]:rod('Guard_post',(cx+dx,y,42.15),(cx+dx,y,43.24),.025)
  for z in [42.68,43.24]:rod('Guard_rail',(cx+dx,-3.85,z),(cx+dx,3.85,z),.025)
 for y in [-3.85,3.85]:
  for z in [42.68,43.24]:rod('Catwalk_end_guard',(cx-.4,y,z),(cx+.4,y,z),.025)
 # Crosshead access walkway joins catwalk at their midpoint, above central steel beam.
 for y in [-.44,.44]:rod('Access_bridge_rail',(0,y,42.72),(cx,y,42.72),.026)
 # Dedicated lifting points, cable detection boxes and beacon pods.
 for y in [-3.6,3.6]:
  rod('Rope_lifting_boom',(cx,y,42.13),(x,y,43.1),.065,dark)
  box('Rope_position_sensor',(x-side*.22,y,42.42),(.16,.19,.14),amber,.015)
 tube('Beacon_base',(cx,0,43.25),(cx,0,43.39),.16,mat=dark)
 tube('Red_marker_lens',(cx,0,43.39),(cx,0,43.63),.12,mat=red)
# Cross access grating at girder top, clear of the outboard cable lanes.
for x in [-5.95+i*.17 for i in range(71)]:box('Bridge_grating',(x,0,41.69),(.04,.9,.065),galv,.004)
for x in [-5.8,-3.5,0,3.5,5.8]:
 for y in [-.44,.44]:rod('Bridge_guard',(x,y,41.7),(x,y,42.72),.026)
# Export specification. Separate editable original and consolidated export copies.
scene['Design']='Maldek modern twin tubular pylon / 42 m study / cylinder shafts and 12-sheave trains'
scene['Reference']='https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/'
scene['Route_placement']='Pending actual Unreal terrain and cable alignment. Studio cable samples are NOT exported.'
# Studio cable samples and human scale figure.
current=stage
for x in [-7.1,7.1]:rod('STUDY_cable',(x,-32,42.327),(x,32,42.327),.032,dark)
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
 '02_crosshead':camera('CAM_02_Crosshead',(23,-29,49),(0,0,41.2),56),
 '03_base_detail':camera('CAM_03_Base',(10,-16,6),(1,0,3.1),55),
 '04_night':camera('CAM_04_Night',(57,-87,36),(0,0,22),55)}
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
report={'design_height_m':43.63,'rope_height_m':42.327,'base_leg_spacing_m':9.2,'head_rope_gauge_m':14.2,'shaft_diameter_base_m':2.1,'shaft_diameter_top_m':1.42,'sheaves_per_lane':12,'objects':len(objects),'route_status':'standalone study - not imported','sources':[{'url':'https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/','used':'Modular circular tubes, special twin legs, flange joints, sheave trains and catwalks'},{'url':'https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR199_ENG.pdf','used':'550 mm sheave diameter as detail proportion reference'}]}
# Basic evaluated mesh sanity and persistent metric metadata.
deps=bpy.context.evaluated_depsgraph_get();invalid=[];triangles=0
for o in objects:
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles)
 if any(not math.isfinite(c) for v in me.vertices for c in v.co):invalid.append(o.name)
 ev.to_mesh_clear()
assert not invalid;report['evaluated_triangles']=triangles
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Modern_Twin_Pylon.blend'))
# Consolidation by material for UE: one reusable asset, kept separate from authoring scene.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.duplicate();copies=list(bpy.context.selected_objects);bpy.ops.object.convert(target='MESH');bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SM_Maldek_Twin_Pylon_42m';scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'fbx/SM_Maldek_Twin_Pylon_42m.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
bpy.data.objects.remove(mesh,do_unlink=True)
for name,cam in cams.items():
 scene.camera=cam
 if name=='04_night':
  sun.energy=.035;world.node_tree.nodes.get('Background').inputs[1].default_value=.025
  for ob in stage.objects:
   if ob.type=='LIGHT' and ob.data.type=='AREA':ob.data.energy*=.12
  scene.view_settings.exposure=.3
 if name=='02_crosshead':scene.render.resolution_x=1800;scene.render.resolution_y=1200
 elif name=='03_base_detail':scene.render.resolution_x=1500;scene.render.resolution_y=1100
 else:scene.render.resolution_x=1500;scene.render.resolution_y=1700
 scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('PYLON_STUDY_COMPLETE',json.dumps(report))
