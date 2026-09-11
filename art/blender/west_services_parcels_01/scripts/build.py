import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; SRC=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend'
ORIGIN=Vector((-37.45,-5,4.6))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==json.loads((SRC.parent/'delivery.json').read_text())['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='WSP_Local';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WSP_ASSETS');s.collection.children.link(C)
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);return o
def mat(n,col,metal=0,rough=.5,grain=False):
 m=bpy.data.materials.new('WSP_'+n);m.diffuse_color=(*col,1);m.use_nodes=True
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if grain:
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4;tex.inputs['Detail'].default_value=3
  coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,3,55)
  nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*.65 for v in col),1);ramp.color_ramp.elements[1].color=(*(min(1,v*1.25) for v in col),1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.001;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
 m['provenance']='Original procedural Blender shader; bake required for engine';return m
pine=mat('Pine',(.48,.285,.12),grain=True);petrol=mat('Petrol_enamel',(.035,.16,.145),.25,.34);cream=mat('Cream_enamel',(.8,.76,.6),.12);steel=mat('Galvanized',(.37,.42,.43),.8,.3);black=mat('Rubber_ink',(.018,.024,.022));paper=mat('Paper',(.8,.69,.46));kraft=mat('Kraft',(.43,.25,.105),grain=True);leather=mat('Oxblood_leather',(.18,.045,.027),rough=.7);olive=mat('Canvas',(.18,.21,.10),rough=.9);glass=mat('Glass',(.66,.83,.82),rough=.08);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.85
def box(n,p,d,m,bev=.008,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=link(bpy.context.object);o.name='WSP_'+n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=min(bev,min(d)*.23);mod.segments=3
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if parent:par(o,parent)
 return o
def cyl(n,p,r,depth,m,axis='Z',parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=p);o=link(bpy.context.object);o.name='WSP_'+n;o.data.materials.append(m)
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 if parent:par(o,parent)
 return o
def empty(n,p):
 o=bpy.data.objects.new('WSP_'+n,None);C.objects.link(o);o.location=p;o.empty_display_size=.12;return o
def par(o,p):
 bpy.context.view_layer.update();mw=o.matrix_world.copy();o.parent=p;o.matrix_world=mw
def text(n,t,p,size=.08,face='X',m=cream,parent=None):
 cu=bpy.data.curves.new(n,'FONT');cu.body=t;cu.size=size;cu.extrude=.0006;cu.align_x='CENTER';o=bpy.data.objects.new('WSP_'+n,cu);C.objects.link(o);o.location=p
 if face=='X':o.rotation_euler=(math.pi/2,0,math.pi/2)
 if face=='-X':o.rotation_euler=(math.pi/2,0,-math.pi/2)
 if face=='Y':o.rotation_euler=(math.pi/2,0,math.pi)
 cu.materials.append(m)
 if parent:par(o,parent)
 return o
def bar(n,a,b,r,m,parent=None):
 v=Vector(b)-Vector(a);o=cyl(n,(Vector(a)+Vector(b))/2,r,v.length,m);o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
 if parent:par(o,parent)
 return o
# Entrance: internal hinge axis; closed leaf behind the shell plane.
for y in [1.1375,2.5625]:box('Door_jamb',(5.90,y,1.175),(.27,.075,2.326),pine)
box('Door_head',(5.90,1.85,2.30),(.27,1.35,.10),pine)
box('Threshold',(5.91,1.85,.006),(.32,1.5,.012),steel,.002)
for x in [5.755,6.045]:
 for y in [1.10,2.60]:box('Door_architrave',(x,y,1.2135),(.035,.105,2.433),petrol)
 box('Door_architrave_head',(x,1.85,2.39),(.035,1.395,.08),petrol)
for y in [1.176,2.524]:box('Door_jamb_seal',(5.790,y,1.14),(.058,.024,2.26),black,.002)
box('Door_head_seal',(5.790,1.85,2.25),(.058,1.324,.03),black,.002)
door=empty('Door_hinge',(5.75,1.18,.02));box('Door_leaf',(5.745,1.85,1.137),(.054,1.35,2.226),petrol,.012,door)
for z in [.5,1.61]:box('Door_recess_panel',(5.710,1.85,z),(.014,1.09,.68),pine,.008,door)
for z in [.25,1.1,2.04]:
 cyl('Door_hinge_barrel',(5.746,1.18,z),.019,.11,steel,parent=door)
 box('Door_hinge_fixed',(5.775,1.14,z),(.015,.064,.10),steel,.002)
latch=empty('Door_latch_pivot',(5.694,2.39,1.02));par(latch,door)
cyl('Latch_rosette',(5.703,2.39,1.02),.042,.015,steel,'X',door);bar('Latch_lever',(5.678,2.39,1.02),(5.678,2.25,1.02),.012,steel,latch)
key=empty('Door_key_cylinder',(5.703,2.39,.88));par(key,door);cyl('Key_face',(5.699,2.39,.88),.022,.016,steel,'X',key);box('Key_slot',(5.688,2.39,.88),(.002,.003,.018),black,.0003,key)
cyl('Exterior_latch_rosette',(5.785,2.39,1.02),.042,.020,steel,'X',door);bar('Exterior_latch_lever',(5.810,2.39,1.02),(5.810,2.25,1.02),.012,steel,latch)
cyl('Exterior_key_face',(5.785,2.39,.88),.022,.020,steel,'X',key);box('Exterior_key_slot',(5.797,2.39,.88),(.002,.003,.018),black,.0003,key)
# Window: fixed sash, sliding internal shutter travels toward party wall in X? Hinged pair folds inward.
for y in [3.24,4.56]:box('Window_jamb',(5.91,y,1.525),(.26,.08,1.05),pine)
for z in [1.04,2.01]:box('Window_sill_head',(5.91,3.90,z),(.26,1.24,.08),pine)
box('Window_mullion',(5.945,3.9,1.525),(.055,.035,.89),petrol)
for y in [3.585,4.215]:box('Window_glass',(5.951,y,1.525),(.008,.591,.886),glass,.001)
for y in [3.285,4.515]:box('Window_sash_vertical',(5.948,y,1.525),(.055,.018,.89),petrol,.003)
for z in [1.085,1.965]:box('Window_sash_horizontal',(5.948,3.9,z),(.055,1.212,.018),petrol,.003)
shutters=[]
for i,y in enumerate([3.285,4.515]):
 e=empty('Shutter_'+str(i)+'_hinge',(5.74,y,1.10));shutters.append(e)
 cy=y+(.302 if i==0 else -.302);box('Shutter_panel_'+str(i),(5.726,cy,1.525),(.033,.598,.852),petrol,.006,e)
 for z in [1.2,1.85]:box('Shutter_batten',(5.702,cy,z),(.014,.54,.045),pine,.003,e)
 cyl('Shutter_knob',(5.68,cy,1.46),.022,.035,steel,'X',e)
for x in [5.76,6.045]:
 for y in [3.2,4.6]:box('Window_casing',(x,y,1.525),(.034,.08,1.14),petrol)
 for z in [.995,2.055]:box('Window_casing',(x,3.9,z),(.034,1.32,.07),petrol)
# Counter, real open kneehole and clerk drawer.
box('Counter_top',(5.08,3.95,.93),(1.24,1.40,.065),pine,.018)
for y in [3.31,4.59]:box('Counter_end',(5.18,y,.46),(.96,.055,.87),petrol)
box('Counter_public_apron',(5.62,3.95,.58),(.045,1.22,.59),petrol)
box('Counter_lower_brace',(5.42,3.95,.16),(.08,1.24,.09),pine)
drawer=empty('Clerk_drawer_slide',(5.0,3.67,.76))
box('Drawer_bottom',(5.09,3.64,.717),(.75,.50,.026),pine,parent=drawer)
for y in [3.38,3.90]:box('Drawer_side',(5.09,y,.79),(.75,.027,.12),pine,parent=drawer)
for x in [4.70,5.48]:box('Drawer_front_back',(x,3.64,.79),(.027,.54,.15),petrol,parent=drawer)
bar('Drawer_pull',(4.671,3.53,.81),(4.671,3.70,.81),.013,steel,drawer);cyl('Drawer_key',(4.678,3.79,.8),.018,.012,steel,'X',drawer)
for yy in [3.358,3.922]:box('Drawer_fixed_slide',(5.09,yy,.82375),(.79,.017,.1475),steel,.002)
# Shelf rack: 4 bays x 3 shelf heights, 0.94m spans, accessible supports.
for y in [.43,1.47,2.51,3.55,4.59]:
 for x in [.33,.95]:box('Rack_upright',(x,y,1.16),(.065,.065,2.22),petrol)
for row,z in enumerate([.25,.88,1.51,2.14]):
 for bay in range(4):
  y=.95+bay*1.04;box('Shelf_%s_%s'%(row,bay),(.64,y,z),(.68,.965,.045),pine)
  for yy in [y-.42,y+.42]:
   box('Shelf_angle',(.63,yy,z-.0375),(.63,.027,.03),steel,.003)
  if row<2:text('Bay_number',f'{row*4+bay+1:02d}',(.99,y,z-.015),.074,'X')
for y in [.46,4.56]:bar('Rack_diagonal',(.31,y,.27),(.31,2.51,2.13),.012,steel)
anchors={}
for row in range(2):
 for bay in range(4):
  i=row*4+bay+1;p=(.64,.95+bay*1.04,[.25,.88][row]+.024)
  e=empty(f'DEPOSIT_{i:02d}',p);anchors[e.name]={'position':p,'support':f'WSP_Shelf_{row}_{bay}','usable_dimensions_m':[.58,.86,.56],'approach':[1,0,0],'reach_height_m':p[2]}
def parcel(i,p,kind):
 e=empty('Belonging_'+str(i),p)
 if kind=='case':
  box('Suitcase_body',(p[0],p[1],p[2]+.235),(.43,.72,.46),leather,.06,e)
  for yy in [p[1]-.23,p[1]+.23]:box('Suitcase_strap',(p[0]+.219,yy,p[2]+.235),(.012,.036,.40),paper,.004,e)
  bar('Suitcase_handle',(p[0],p[1]-.10,p[2]+.50),(p[0],p[1]+.10,p[2]+.50),.018,leather,e)
  for yy in [p[1]-.10,p[1]+.10]:bar('Suitcase_handle_mount',(p[0],yy,p[2]+.44),(p[0],yy,p[2]+.50),.013,steel,e)
  for yy in [p[1]-.25,p[1]+.25]:box('Suitcase_clasp',(p[0]+.222,yy,p[2]+.32),(.013,.053,.04),steel,.003,e)
 else:
  box('Canvas_bag' if kind=='bag' else 'Wrapped_parcel',(p[0],p[1],p[2]+.18),(.45,.60,.36),olive if kind=='bag' else kraft,.08 if kind=='bag' else .014,e)
  for yy in [p[1]-.17,p[1]+.17]:box('Strap_string',(p[0]+.229,yy,p[2]+.18),(.009,.012,.33),paper,.002,e)
  if kind=='bag':
   bar('Bag_handle',(p[0],p[1]-.12,p[2]+.41),(p[0],p[1]+.12,p[2]+.41),.014,olive,e)
   for yy in [p[1]-.12,p[1]+.12]:bar('Bag_handle_loop',(p[0],yy,p[2]+.33),(p[0],yy,p[2]+.41),.012,olive,e)
 box('Property_tag',(p[0]+.242,p[1]+.12,p[2]+.25),(.007,.13,.072),paper,.003,e);text('Tag_id',f'{i:02d}',(p[0]+.247,p[1]+.12,p[2]+.228),.041,'X',black,e)
 bar('Tag_tie',(p[0]+.21,p[1]+.12,p[2]+.345),(p[0]+.242,p[1]+.12,p[2]+.28),.002,paper,e)
 return e
props=[]
for i,kind in [(1,'case'),(3,'parcel'),(5,'bag'),(6,'parcel'),(8,'bag')]:props.append(parcel(i,anchors[f'WSP_DEPOSIT_{i:02d}']['position'],kind))
# South secure cabinet: open structural box, individual trays and mesh door.
for x in [1.48,2.92]:box('Secure_side',(x,.59,1.02),(.05,.58,1.94),petrol)
box('Secure_back',(2.20,.315,1.02),(1.39,.03,1.94),petrol)
for z in [.08,.65,1.24,1.97]:box('Secure_shelf',(2.2,.60,z),(1.39,.54,.033),pine)
trays=[]
for i,z in enumerate([.11,.68,1.27]):
 e=empty(f'Secure_tray_{i+1}_slide',(2.2,.60,z));trays.append(e)
 for xx in [1.60,2.80]:box('Secure_tray_fixed_runner',(xx,.59,z-.0055),(.030,.40,.016),steel,.002)
 box('Tray_base',(2.2,.59,z+.015),(1.27,.48,.025),steel,.004,e)
 for x in [1.56,2.84]:box('Tray_side',(x,.59,z+.064),(.016,.48,.10),steel,.003,e)
 for y in [.343,.837]:box('Tray_lip',(2.2,y,z+.064),(1.296,.014,.10),steel,.002,e)
 text('Tray_label',f'S{i+1}  /  SECURE',(2.2,.845,z+.039),.057,'Y',cream,e)
cab=empty('Secure_door_hinge',(1.51,.90,.08))
for x in [1.53,2.87]:box('Secure_door_stile',(x,.9,1.03),(.035,.04,1.90),steel,.004,cab)
for z in [.095,1.965]:box('Secure_door_rail',(2.2,.9,z),(1.31,.04,.035),steel,.004,cab)
for i in range(25):box('Secure_wire_vertical',(1.57+i*.0525,.9,1.03),(.004,.004,1.825),steel,.0005,cab)
for i in range(34):box('Secure_wire_horizontal',(2.2,.906,.14+i*.054),(1.29,.004,.004),steel,.0005,cab)
box('Secure_lock_plate',(2.81,.927,1.03),(.10,.019,.14),petrol,.007,cab);cyl('Secure_key',(2.81,.944,1.04),.022,.023,steel,'Y',cab);box('Secure_key_slot',(2.81,.96,1.04),(.003,.003,.023),black,.001,cab)
for z in [.30,1.70]:cyl('Secure_hinge',(1.51,.9,z),.018,.11,steel,parent=cab)
# Trolley .8 x 1.2, four caster swivels, wheel axle pivots.
trolley=empty('Trolley_root',(3.66,.86,0));box('Trolley_deck',(3.66,.86,.23),(.72,1.10,.055),pine,.025,trolley)
for x in [3.34,3.98]:
 for y in [.36,1.36]:
  sw=empty('Caster_swivel',(x,y,.20));par(sw,trolley);cyl('Caster_race',(x,y,.196),.05,.032,steel,parent=sw)
  for xx in [x-.04,x+.04]:box('Caster_fork',(xx,y,.13),(.015,.09,.13),steel,.004,sw)
  wh=empty('Wheel_axle',(x,y,.085));par(wh,sw);cyl('Trolley_tyre',(x,y,.085),.079,.06,black,'X',wh);cyl('Trolley_hub',(x,y,.085),.025,.067,steel,'X',wh)
for x in [3.34,3.98]:bar('Trolley_handle_post',(x,.34,.26),(x,.34,1.02),.021,steel,trolley)
bar('Trolley_grip',(3.34,.34,1.02),(3.98,.34,1.02),.026,black,trolley)
# Analog counter props, all independent.
box('Scale_base',(5.06,4.28,1.02),(.46,.48,.10),petrol,.035)
box('Scale_neck',(5.22,4.28,1.20),(.11,.14,.31),petrol,.015)
cyl('Scale_dial_rim',(4.99,4.28,1.23),.135,.055,steel,'X');cyl('Scale_dial',(4.956,4.28,1.23),.12,.009,cream,'X')
for i in range(11):
 a=math.radians(-130+i*26);y=4.28+math.sin(a)*.096;z=1.23+math.cos(a)*.096
 bar('Scale_tick',(4.949,y,z),(4.949,4.28+math.sin(a)*.083,1.23+math.cos(a)*.083),.0018,black)
bar('Scale_pointer',(4.940,4.28,1.23),(4.940,4.22,1.30),.003,black);text('Scale_units','kg',(4.937,4.28,1.175),.024,'-X',black)
box('Scale_pan',(5.20,4.28,1.413),(.44,.43,.022),steel,.014)
for o in C.objects:
 if o.name.startswith('WSP_Scale'):o.location.x-=.32
box('Ledger_cover',(4.92,3.76,.978),(.46,.32,.018),leather,.007);box('Ledger_pages',(4.92,3.76,.994),(.435,.29,.012),paper,.002)
for i in range(8):box('Ledger_rule',(4.92,3.65+i*.03,1.0005),(.37,.001,.0006),black,0)
box('Ledger_spine',(4.92,3.76,1.003),(.005,.29,.003),leather,.001)
box('Tag_dispenser',(5.28,3.42,1.02),(.25,.22,.11),petrol,.012)
for i in range(6):box('Blank_tag',(5.24,3.42,1.079+i*.0018),(.15,.085,.0014),paper,.0001)
cyl('String_spool',(5.40,3.70,1.04),.043,.12,paper)
for z in [.978,1.105]:cyl('Spool_flange',(5.40,3.70,z),.052,.008,pine)
box('Stamp_pad',(4.80,3.42,.982),(.13,.09,.026),black,.008);cyl('Stamp_handle',(4.95,3.42,1.017),.019,.08,pine)
for i in range(2):bar('Pencil',(4.72+i*.04,3.56,.974),(4.78+i*.04,3.72,.974),.004,paper)
for ob in C.objects:
 if ob.name.startswith('WSP_Pencil'):ob.location.x-=.16;ob.location.z-=.007
 if ob.name.startswith('WSP_Ledger'):ob.location.z-=.0065
 if ob.name.startswith('WSP_Scale'):ob.location.z-=.0075
 if ob.name.startswith(('WSP_String_spool','WSP_Spool_flange')):ob.location.z-=.0115
 if ob.name.startswith('WSP_Tag_dispenser'):ob.location.z-=.0025
 if ob.name.startswith('WSP_Blank_tag'):ob.location.z-=.0058
box('Stamp_foot',(4.95,3.42,.973),(.060,.045,.021),black,.004)
box('Exterior_sign_board',(6.035,1.85,2.57),(.035,1.66,.26),cream,.012);text('Exterior_sign','PARCELS  /  LEFT LUGGAGE',(6.057,1.85,2.54),.085,'X',petrol)
box('Secure_sign_board',(2.2,.342,2.17),(1.32,.027,.21),cream);text('Secure_sign','TAGGED PROPERTY',(2.2,.365,2.145),.094,'Y',petrol)
for n,p,approach in [('TAG_STATION',(4.88,3.42,1.10),(-1,0,0)),('LOG_LEDGER',(4.92,3.76,1.04),(-1,0,0)),('SECURE_CABINET',(2.20,1.05,1.05),(0,1,0)),('TROLLEY_PARK',(3.66,.86,.25),(0,1,0))]:
 empty(n,p);anchors['WSP_'+n]={'position':p,'approach':approach,'reach_height_m':p[2],'usable_dimensions_m':[.6,.6,.5]}
marker=empty('ORIENTATION_EAST_PLUS_X',(6.4,1.85,.1));marker['direction']='+X east toward porch; north +Y'
# Linear/rotary animation serves as editable state demonstration, no runtime code.
mechanisms=[]
def motion(o,kind,axis,amount):
 prop='rotation_euler' if kind=='ROTATION' else 'location';base=getattr(o,prop)[axis]
 keys=[(1,base),(40,base+amount),(80,base)]
 if o.name=='WSP_Secure_door_hinge':keys=[(1,base),(20,base+amount),(60,base+amount),(80,base)]
 if o.name.startswith('WSP_Secure_tray'):keys=[(1,base),(20,base),(40,base+amount),(60,base),(80,base)]
 for f,val in keys:
  getattr(o,prop)[axis]=val;o.keyframe_insert(data_path=prop,index=axis,frame=f)
 mechanisms.append({'object':o.name,'kind':kind,'axis':axis,'rest':base,'open':base+amount,'pivot_parent_space_m':list(o.location),'frames':{'closed':1,'open':40,'rest':80}})
motion(door,'ROTATION',2,math.pi/2);motion(latch,'ROTATION',0,.4);motion(key,'ROTATION',0,math.pi/2)
motion(drawer,'TRANSLATION',0,-.38);motion(cab,'ROTATION',2,math.pi/2)
for i,e in enumerate(shutters):motion(e,'ROTATION',2,math.pi/2 if i==0 else -math.pi/2)
for e in trays:motion(e,'TRANSLATION',1,.25)
for o in list(C.objects):
 if 'Caster_swivel' in o.name:motion(o,'ROTATION',2,math.pi/2)
 if 'Wheel_axle' in o.name:motion(o,'ROTATION',0,math.pi)
s.frame_set(1)
# Usable independent smart UVs; font outlines retained editable.
for o in C.objects:
 if o.type=='MESH':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
assembly={'units':'metres','collection':'WSP_ASSETS','asset_blend':'Maldek_Parcels_Office.blend','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'local_to_world':[[1,0,0,-37.45],[0,1,0,-5],[0,0,1,4.6],[0,0,0,1]],'orientation_marker':marker.name,'replacement_collection':'WS_PARCELS_PROXY','delete_exact':json.loads((SRC.parent/'manifest.json').read_text())['collections']['WS_PARCELS_PROXY'],'anchors':anchors,'mechanisms':mechanisms,'clear_door_m':[1.35,2.238],'handling_zone_local':[[2.05,1.6,0],[4.25,3.8,2.2]],'operator_aisle_local':[[3.3,3.25,0],[4.55,4.7,2.2]],'trolley_envelope_m':[.8,1.2,1.1],'export':{'include_collection_only':'WSP_ASSETS','exclude_types':['EMPTY (except pivots/anchors)','CAMERA','LIGHT'],'rotation':[0,0,0],'scale':[1,1,1],'engine_export_pending':True},'materials':{m.name:{'procedural':True,'slots':[m.name]} for m in bpy.data.materials},'limitations':['Engine collision and actual capsule traversal untested','Procedural material baking, export and LOD work remain integration gates']}
assembly['clear_door_m']=[1.324,2.223]
assembly['operator_aisle_local']=[[3.0,3.25,0],[4.25,4.7,2.2]]
assembly['operator_aisle_clear_width_m']=1.25
assembly['secure_sequence']='Door opens frames 1-20, stays open through 60; trays extend 20-40 and retract 40-60; door closes 60-80.'
assembly['surface_ownership']={'shared_shell_patch':None,'reason':'Frames span entire shell thickness; butt interfaces concealed beneath separate casings. No new wall skins or duplicated floor. Seals bridge to closed leaf.'}
(P/'assembly.json').write_text(json.dumps(assembly,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Parcels_Office.blend'))
print('ASSET_SAVED',len(C.objects))
