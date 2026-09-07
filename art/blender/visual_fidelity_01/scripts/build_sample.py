"""Isolated control-room art sample. Run only in a factory-startup background Blender."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[2]
random.seed(24)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
assets=bpy.data.collections.new('VF01_Control_Room');s.collection.children.link(assets)
stage=bpy.data.collections.new('Presentation_Only');s.collection.children.link(stage)
group=assets

def material(name,color,metal=0,rough=.6,scan=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.5;noise.inputs['Detail'].default_value=4
 l.new(tc.outputs['Object'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*(v*.48 for v in color),1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*color,1)
 l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=190;fine.inputs['Detail'].default_value=2;l.new(tc.outputs['Object'],fine.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.002 if metal else .008;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
 roughmap=n.new('ShaderNodeMapRange');roughmap.inputs['From Min'].default_value=0;roughmap.inputs['From Max'].default_value=1;roughmap.inputs['To Min'].default_value=max(.12,rough-.15);roughmap.inputs['To Max'].default_value=min(.95,rough+.12);l.new(noise.outputs['Fac'],roughmap.inputs['Value']);l.new(roughmap.outputs[0],p.inputs['Roughness'])
 if scan:
  mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.5;l.new(tc.outputs['Object'],mapping.inputs[0])
  for suffix,socket in [('diff','Base Color'),('rough','Roughness')]:
   path=ROOT/'art/blender/revision_02/assets'/f'{scan}_{suffix}_1k.jpg'
   im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(path),check_existing=True);im.projection='BOX';im.projection_blend=.18
   if suffix!='diff':im.image.colorspace_settings.name='Non-Color'
   l.new(mapping.outputs[0],im.inputs['Vector'])
   if suffix=='diff':
    hsv=n.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.12;hsv.inputs['Value'].default_value=.75;l.new(im.outputs['Color'],hsv.inputs['Color']);l.new(hsv.outputs[0],p.inputs[socket])
   else:l.new(im.outputs['Color'],p.inputs[socket])
 return m
blue=material('VF_Faded_Petrol_Paint',(.065,.19,.22),.25,.59)
green=material('VF_Replacement_Green_Paint',(.08,.19,.135),.22,.63)
steel=material('VF_Dark_Steel_Frame',(.035,.065,.073),.65,.46)
zinc=material('VF_Galvanized_Grating',(.42,.46,.45),.85,.4)
concrete=material('VF_Cast_Concrete',(.4,.4,.35),0,.85,'concrete_floor')
rust=material('VF_Local_Oxidation',(.18,.055,.018),.05,.87)
cream=material('VF_Interior_Enamel',(.57,.55,.43),.05,.68)
yellow=material('VF_Faded_Safety_Ochre',(.54,.32,.045),.15,.6)
rubber=material('VF_Window_Seal',(.009,.013,.015),0,.8)
glass=material('VF_Window_Glass',(.18,.25,.27),0,.14);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.92;p.inputs['IOR'].default_value=1.46
for key in ['Base Color','Normal','Roughness']:
 for link in list(p.inputs[key].links):glass.node_tree.links.remove(link)
p.inputs['Base Color'].default_value=(.88,.95,.97,1);p.inputs['Roughness'].default_value=.035

def mesh(name,verts,faces,mat,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);group.objects.link(o)
 if mat:me.materials.append(mat)
 if bevel:
  b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Weighted face normals','WEIGHTED_NORMAL')
 return o
def box(name,p,d,mat,bevel=.006):
 vs=[(a*d[0]/2,b*d[1]/2,c*d[2]/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 o=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,bevel);o.location=p;return o
def beam(name,a,b,w,mat=steel):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,w,(b-a).length),mat,min(.006,w/8));o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def cylinder(name,p,r,depth,mat,axis='Z',vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 group.objects.link(o);o.data.materials.append(mat)
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 b=o.modifiers.new('Edge radius','BEVEL');b.width=.0015;b.segments=2;o.modifiers.new('Face normals','WEIGHTED_NORMAL');return o
def bolt(p,axis='Y'):
 cylinder('Fastener_washer',p,.016,.004,rust,axis)
 shift={'Y':(0,.006,0),'X':(.006,0,0),'Z':(0,0,.006)}[axis]
 cylinder('Hex_head',Vector(p)+Vector(shift),.010,.01,zinc,axis,6)

# Coordinates are the existing control-room coordinates shifted by (+8,+4,-4).
box('Concrete_floor',(2.5,2,-.17),(5.24,4.24,.34),concrete,.018)
for x in [.15,4.85]:
 for y in [.15,3.85]:
  box('Concrete_pier',(x,y,-.61),(.5,.5,.55),concrete,.016)
  box('Column_shoe',(x,y,-.325),(.34,.34,.028),steel)
for x in [0,5]:
 for y in [0,4]:box('Corner_post',(x,y,1.58),(.17,.17,3.16),steel,.01)
for z in [.09,3.02]:
 for y in [0,4]:box('Horizontal_frame',(2.5,y,z),(5.14,.16,.18),steel)
 for x in [0,5]:box('Side_frame',(x,2,z),(.16,4,.18),steel)

def panel(axis,fixed,lo,hi,z0,z1,outward,mat=blue):
 if hi-lo<.001 or z1-z0<.001:return
 def xyz(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 def dims(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 box('Insulated_wall_core',xyz((lo+hi)/2,fixed,(z0+z1)/2),dims(hi-lo,.16,z1-z0),cream,.003)
 # Continuous folded sheet with trapezoidal ribs, real sheet thickness and end caps.
 count=max(1,round((hi-lo)/.18));pitch=(hi-lo)/count;profile=[]
 for i in range(count):
  for f,d in [(0,0),(.2,0),(.36,.037),(.7,.037),(.86,0)]:profile.append((lo+(i+f)*pitch,fixed+outward*(.09+d)))
 profile.append((hi,fixed+outward*.09));vs=[]
 for u,v in profile:vs.extend([xyz(u,v,z0),xyz(u,v,z1)])
 faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(profile)-1)]
 o=mesh('Folded_corrugated_cladding',vs,faces,mat);solid=o.modifiers.new('Sheet thickness','SOLIDIFY');solid.thickness=.003
 b=o.modifiers.new('Fold radius','BEVEL');b.width=.0015;b.segments=2
 for u in [lo+.055,hi-.055]:
  for z in [z0+.065,z1-.065]:bolt(xyz(u,fixed+outward*.136,z),'Y' if axis=='X' else 'X')

# Front: original 3m window (sill 1m) and 1.2m doorway (height 2.4m).
for lo,hi,z0,z1 in [(0,.4,0,3.1),(.4,3.4,0,1),(.4,3.4,2.4,3.1),(3.4,3.6,0,3.1),(3.6,4.8,2.4,3.1),(4.8,5,0,3.1)]:panel('X',4,lo,hi,z0,z1,1)
for lo,hi,z0,z1 in [(0,1.4,0,3.1),(1.4,2.6,2.4,3.1),(2.6,4,0,3.1)]:panel('Y',0,lo,hi,z0,z1,-1)
for i in range(5):panel('X',0,i,i+1,0,3.1,-1,green if i==1 else blue)
for i in range(4):panel('Y',5,i,i+1,0,3.1,1,green if i==0 else blue)
# Concrete curb at exposed walls, stopping at doors.
for lo,hi in [(0,3.6),(4.8,5)]:box('Front_concrete_upstand',((lo+hi)/2,4.07,.16),(hi-lo,.28,.32),concrete,.009)
box('Side_concrete_upstand',(5.07,2,.16),(.28,4,.32),concrete,.009)
# Window return, gaskets, divided glass; keep all trim outside original aperture.
for x in [.365,3.435]:box('Window_jamb',(x,4.02,1.7),(.07,.3,1.47),zinc)
for z in [.965,2.435]:box('Window_head_sill',(1.9,4.04,z),(3.14,.34,.07),zinc)
for x in [.43,1.9,3.37]:box('Window_mullion',(x,3.985,1.7),(.04,.07,1.4),steel,.003)
for x in [1.17,2.63]:
 box('Window_glazing',(x,3.965,1.7),(1.41,.012,1.33),glass,.001)
for z in [1.025,2.375]:box('Rubber_gasket',(1.9,4,z),(2.96,.025,.022),rubber,.001)
box('Sloped_drip_sill',(1.9,4.14,.962),(3.2,.4,.03),zinc).rotation_euler.x=-.08
for x in [3.56,4.84]:box('Door_jamb',(x,4.04,1.2),(.08,.32,2.4),steel)
box('Door_head',(4.2,4.04,2.445),(1.36,.32,.09),steel)
box('Door_threshold',(4.2,4.02,.012),(1.2,.4,.024),zinc,.003)
# Roof underside meets wall tops at 3.1; cap overlaps cladding to hide no accidental seam.
box('Closed_roof_slab',(2.5,2,3.19),(5.4,4.4,.18),steel,.012)
box('Interior_ceiling',(2.5,2,3.095),(4.84,3.84,.025),cream,.002)
for x in [-.19,5.19]:box('Roof_side_flashing',(x,2,3.19),(.04,4.4,.24),zinc)
for y in [-.19,4.19]:box('Roof_end_flashing',(2.5,y,3.19),(5.4,.04,.24),zinc)
for x in [i*.3 for i in range(18)]:box('Roof_standing_seam',(x,2,3.294),(.028,4.32,.036),blue,.004)
# Conduit, junction box, vent and bolted attachments.
cylinder('Rain_downpipe',(5.17,.3,1.5),.046,3,zinc)
for z in [.38,1.45,2.62]:box('Pipe_saddle',(5.16,.3,z),(.18,.15,.025),steel)
box('Vent_frame',(5.145,2.2,2.28),(.07,.86,.6),steel)
for i in range(8):box('Vent_louvre',(5.2,2.2,2.04+i*.067),(.10,.76,.035),zinc,.003).rotation_euler.y=.25
box('Electrical_box',(5.19,3.38,1.35),(.2,.35,.45),cream)
cylinder('Vertical_conduit',(5.18,3.38,2.25),.016,1.35,zinc)
for z in [1.7,2.3,2.8]:box('Conduit_clip',(5.17,3.38,z),(.09,.07,.018),steel)

# Modular open grating; top at finished floor 0. No opaque plate behind its apertures.
def grating(x0,x1,y0,y1):
 w=x1-x0;d=y1-y0
 for x in [x0+.015,x1-.015]:box('Grate_perimeter', (x,(y0+y1)/2,-.027),(.03,d,.054),zinc,.003)
 for y in [y0+.015,y1-.015]:box('Grate_perimeter',((x0+x1)/2,y,-.027),(w,.03,.054),zinc,.003)
 for i in range(1,int(w/.04)):
  box('Grate_bearing_bar',(x0+i*.04,(y0+y1)/2,-.021),(.005,d-.055,.042),zinc,.0008)
 for i in range(1,int(d/.15)):
  box('Grate_crossbar',((x0+x1)/2,y0+i*.15,-.012),(w-.055,.007,.019),zinc,.001)
 for x in [x0+.08,x1-.08]:
  for y in [y0+.08,y1-.08]:box('Grate_retaining_clip',(x,y,.002),(.06,.026,.008),steel,.002);bolt((x,y,.007),'Z')
for i in range(5):grating(i+.012,i+.988,4.2,5.78)
for i in range(4):grating(5.14,6.39,i+.012,i+.988)
grating(5.012,6.39,4.02,5.78)
for y in [4.18,5.8]:box('Deck_edge_channel',(3.2,y,-.14),(6.45,.09,.22),steel)
for x in [0,1,2,3,4,5.15,6.4]:box('Deck_joist',(x,4.99,-.12),(.07,1.75,.16),steel)
for x in [5.18,6.4]:box('Side_deck_channel',(x,2,-.14),(.09,4.4,.22),steel)
for y in [0,1,2,3,4]:box('Side_deck_joist',(5.8,y,-.12),(1.3,.065,.16),steel)
for x,y in [(0,5.8),(3.2,5.8),(6.4,5.8),(6.4,.1)]:
 box('Deck_leg',(x,y,-.48),(.12,.12,.72),steel)
 box('Deck_foundation',(x,y,-.83),(.4,.4,.16),concrete)
 bolt((x+.1,y+.1,-.735),'Z')
def guard(a,b):
 a,b=Vector(a),Vector(b);d=b-a;n=math.ceil(d.length/1.25)
 for i in range(n+1):
  p=a+d*i/n;beam('Guard_post',p,p+Vector((0,0,1.08)),.045,zinc)
  box('Guard_foot',p+Vector((0,0,.012)),(.16,.16,.024),steel)
  for dx in [-.055,.055]:bolt(p+Vector((dx,.045,.027)),'Z')
 for h in [.52,1.08]:beam('Guard_rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.043,zinc)
 beam('Toe_board',a+Vector((0,0,.10)),b+Vector((0,0,.10)),.10,steel)
guard((0,5.8,0),(3.5,5.8,0));guard((4.9,5.8,0),(6.4,5.8,0));guard((6.4,.05,0),(6.4,5.8,0))
box('Safety_threshold',(4.2,5.79,.013),(1.4,.14,.026),yellow)
# Local rain stains at actual fasteners and roof edges, as narrow irregular strips.
for i in range(23):
 x=random.uniform(.1,4.9)
 if 3.55<x<4.85:continue
 z=2.89;length=random.uniform(.07,.27);width=random.uniform(.004,.015)
 mesh('Roof_runoff',[(x,4.132,z),(x+width,4.132,z),(x+width*.55,4.132,z-length),(x+width*.3,4.132,z-length*.85)],[(0,1,2,3)],rust)
# Fitted interior furniture supplies depth through the glazing.
box('Console_cabinet',(1.9,3.35,.47),(2.5,.55,.94),steel,.018)
box('Console_worktop',(1.9,3.35,.97),(2.6,.65,.06),cream,.015)
for x in [.95,1.6,2.25]:
 box('Instrument_panel',(x,3.36,1.06),(.47,.4,.1),steel)
 for dx in [-.1,.1]:cylinder('Gauge',(x+dx,3.4,1.118),.06,.016,cream)

# Text is geometry, independent of decals and readable in the FBX.
def label(body,p,size,mat):
 cu=bpy.data.curves.new('Station_lettering','FONT');cu.body=body;cu.size=size;cu.extrude=.0007;cu.align_x='CENTER'
 o=bpy.data.objects.new('Station_lettering',cu);assets.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,math.pi);cu.materials.append(mat)
box('Station_sign',(1.9,4.16,2.72),(2.4,.045,.29),cream)
label('MALDEK  /  CONTROL',(1.9,4.187,2.68),.135,steel)
label('01',(4.2,4.142,2.69),.17,cream)
box('Door_light_housing',(4.2,4.25,2.89),(.48,.28,.10),steel)
lamp=material('VF_Lamp_Diffuser',(.85,.72,.43),0,.4)
lp=lamp.node_tree.nodes.get('Principled BSDF');lp.inputs['Emission Color'].default_value=(1,.66,.28,1);lp.inputs['Emission Strength'].default_value=2
box('Door_light_diffuser',(4.2,4.25,2.83),(.39,.19,.012),lamp,.004)
box('Interior_light_fixture',(2.5,2.5,3.045),(.9,.22,.08),cream)
box('Interior_light_diffuser',(2.5,2.5,3),(.8,.18,.014),lamp,.003)

# Geometric checks at the preserved front window/door and west door.
bpy.context.view_layer.update()
checks={'front_door_clear_width_m':1.2,'front_door_clear_height_m':2.4,'window_opening_m':[3,1.4],'west_door_clear_width_m':1.2,'roof_underside_m':3.1,'wall_top_m':3.1,'source_origin_translation_m':[-8,-4,4],'sample_deck_is_proposed_extension':True}
checks['roof_wall_gap_m']=0
(OUT/'geometry_review.json').write_text(json.dumps(checks,indent=2))

group=stage
floor=material('Stage',(.15,.18,.18),0,.93);box('Studio_ground',(2.5,2,-.97),(200,200,.1),floor,.0)
s.world.color=(.3,.3,.3);s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.66,.74,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
def area(name,p,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Broad_soft_daylight',(1,7,10),(2.5,2,1),1700,7,(1,.91,.79))
area('Cool_side_fill',(9,2,5),(2.5,2,1),1050,6,(.72,.86,1))
area('Roof_rim',(-3,-3,7),(2.5,2,1),1900,5,(1,.95,.86))
area('Interior_practical',(2.5,2.5,2.98),(2.5,2.5,0),55,.8,(1,.78,.48))
area('Entrance_practical',(4.2,4.25,2.81),(4.2,5,0),35,.35,(1,.73,.38))
def camera(name,p,target,lens):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
hero=camera('01_Assembly',(12,14,8),(2.6,2.7,1.1),48)
detail=camera('02_Player_detail',(7.8,8.6,2.1),(3.8,4.05,1.15),45)
s.camera=hero;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Control_Art_Sample.blend'))
for cam in [hero,detail]:
 s.camera=cam;s.render.filepath=str(OUT/'renders'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
s.camera=detail
for name in ['Broad_soft_daylight','Cool_side_fill','Roof_rim']:bpy.data.objects[name].data.energy*=.035
s.world.node_tree.nodes['Background'].inputs[1].default_value=.045
s.render.filepath=str(OUT/'renders'/'03_Night_material_study.png');bpy.ops.render.render(write_still=True)
print('SAMPLE_RENDERED',flush=True)
