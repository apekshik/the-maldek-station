"""Editable cabin study: retained envelope, paired sliding doors, interior fit-out."""
import bpy,math,json,ast,random,runpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
with bpy.data.libraries.load(str(OUT.parent/'visual_fidelity_07/Maldek_Station_Cleanup.blend'),link=False) as (a,b):b.collections=['12_Gondola','VF06_Gondola_Details']
for c in b.collections:
 s.collection.children.link(c);c.hide_render=False;c.hide_viewport=False
bpy.context.view_layer.update()
initial_world={o:o.matrix_world.copy() for o in s.objects}
# Work in cabin coordinates: floor top is Z=0; boarding end faces -Y.
removed=[]
for o in list(s.objects):
 o.parent=None;o.matrix_world=initial_world[o]
 o.hide_render=False;o.hide_set(False)
 if o.name.startswith(('Door_track','R04_Boarding_Grab_Handle','R04_Handle_Mount','Upholstered_bench_pad','R04_Boarding_Sill')) or o.name=='MIND THE GAP':
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True);continue
 o.location-=Vector((0,8.05,4))
for node in ast.parse((OUT.parent/'door_study_01/scripts/build_door.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['mat','link','box','cyl','rod','text']:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
def col(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
fixed=col('01_Door_fixed_track_and_drive');left=col('02_Left_sliding_leaf');right=col('03_Right_sliding_leaf');interior=col('04_Cabin_interior_details');controls=col('05_Animation_controls');studio=col('90_Review_studio')
green=mat('GC01_Petrol_enamel',(.045,.135,.12),.35,.48);cream=mat('GC01_Warm_enamel',(.57,.51,.37),.16,.58);metal=mat('GC01_Brushed_metal',(.28,.31,.30),.85,.32);dark=mat('GC01_Graphite',(.022,.028,.027),.30,.7);rubber=mat('GC01_Seal_rubber',(.012,.016,.015),0,.88);amber=mat('GC01_Faded_ochre',(.46,.27,.065),.16,.64);vinyl=mat('GC01_Olive_vinyl',(.075,.085,.055),0,.68);ink=mat('GC01_Lettering',(.75,.67,.47),.03,.62);red=mat('GC01_Emergency_red',(.30,.028,.014),.16,.60);glass=mat('GC01_Laminated_glass',(.67,.81,.76),0,.12)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1;glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
for m in [green,cream,metal,vinyl]:
 n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=180;bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.00015;m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
for o in s.objects:
 if o.type not in {'MESH','FONT','CURVE'}:continue
 for slot in o.material_slots:
  n=slot.material.name if slot.material else ''
  if 'Glass' in n or 'glass' in n:slot.material=glass
  elif 'Oxide' in n or 'Petrol' in n:slot.material=green
  elif 'Galvan' in n:slot.material=metal
  elif 'Charcoal' in n:slot.material=dark
  elif 'Rubber' in n:slot.material=rubber
  elif 'enamel' in n.lower():slot.material=cream
def empty(name,p):
 o=bpy.data.objects.new(name,None);controls.objects.link(o);o.location=p;o.empty_display_type='ARROWS';o.empty_display_size=.15;return o
def parent_keep(o,p):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
def screw(x,y,z,front=True):
 cyl('GC_Fastener',(x,y,z),.006,.004,metal,'Y',16);box('GC_Slotted_head',(x,y+(-.0023 if front else .0023),z),(.007,.0007,.0012),dark,.0002)
def tube(name,points,r,m):
 closed=points[0]==points[-1];points=points[:-1] if closed else points
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;cu.use_fill_caps=not closed;sp=cu.splines.new('POLY');sp.use_cyclic_u=closed;sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);group.objects.link(ob);cu.materials.append(m);return ob
group=fixed
# Existing doorway is 1.20m wide x 2.10m high. Leaves run outside the old jambs.
box('GC_Sill_replacement',(0,-3.025,-.012),(1.20,.34,.024),metal,.002)
for x in [-.625,.625]:box('GC_Jamb_seal',(x,-3.105,1.05),(.025,.012,2.07),rubber,.004)
box('GC_Top_seal',(0,-3.105,2.115),(1.20,.012,.025),rubber,.004)
for x in [-1.40,1.40]:
 rod('GC_Outboard_boarding_handle',(x,-3.23,.80),(x,-3.23,1.33),.018,metal)
 for z in [.80,1.33]:rod('GC_Handle_return',(x,-3.23,z),(x,-3.075,z),.018,metal);cyl('GC_Handle_mount',(x,-3.08,z),.032,.01,green,'Y')
box('GC_Track_backplate',(0,-3.105,2.195),(2.68,.012,.18),dark,.004)
rod('GC_Guide_rail',(-1.31,-3.16,2.185),(1.31,-3.16,2.185),.013,metal)
for x in [-1.33,1.33]:box('GC_End_stop',(x,-3.17,2.19),(.025,.11,.17),rubber,.003)
for x in [-1.20,-.60,0,.60,1.20]:
 box('GC_Track_standoff',(x,-3.095,2.19),(.045,.022,.16),metal,.003);screw(x,-3.225,2.255)
cover=box('GC_Removable_drive_guard',(0,-3.245,2.235),(2.73,.026,.13),green,.006)
box('GC_Guard_top',(0,-3.165,2.295),(2.73,.18,.016),green,.003)
text('GC_Guard_plate','AUTOMATIC DOORS  /  KEEP CLEAR',(0,-3.26,2.225),.042,ink)
# Visible opposed rack segments and pinion, with end stops and supported bearings.
pinion=empty('GC_DRIVE_PINION',(0,-3.125,2.185))
wheel=cyl('GC_Pinion',(0,-3.125,2.185),.031,.026,metal,'Y',40);parent_keep(wheel,pinion)
for i in range(16):
 a=i*math.tau/16;o=box('GC_Pinion_tooth',(.034*math.cos(a),-3.125,2.185+.034*math.sin(a)),(.010,.025,.008),metal,.001);o.rotation_euler.y=-a;parent_keep(o,pinion)
box('GC_Gearmotor_case',(.95,-3.12,2.185),(.22,.075,.11),dark,.018)
rod('GC_Enclosed_drive_shaft',(.02,-3.12,2.185),(.84,-3.12,2.185),.009,metal)
box('GC_Right_angle_drive',(0,-3.125,2.185),(.065,.065,.060),dark,.012)
for x in [.87,.92,.97,1.02]:box('GC_Motor_cooling_rib',(x,-3.166,2.185),(.008,.018,.092),metal,.002)
box('GC_Limit_switch_L',(-1.27,-3.20,2.235),(.044,.026,.027),red,.004);box('GC_Limit_switch_R',(1.27,-3.20,2.235),(.044,.026,.027),red,.004)
tube('GC_Protected_wiring',[(1.05,-3.115,2.24),(1.24,-3.115,2.24),(1.30,-3.115,2.20),(1.30,-3.115,2.10)],.006,rubber)
roots=[];rollers=[]
for sign,collection in [(-1,left),(1,right)]:
 group=collection;root=empty('GC_SLIDE_'+('LEFT' if sign<0 else 'RIGHT'),(0,0,0));roots.append(root);xc=sign*.307
 # Individual frame rails surround the glass: no hidden solid panel behind it.
 for x in [sign*.040,sign*.574]:box('GC_Leaf_stile',(x,-3.16,1.05),(.064,.070,2.06),green,.009)
 for z,h in [(.063,.086),(.925,.10),(2.039,.082)]:box('GC_Leaf_crossrail',(xc,-3.16,z),(.47,.070,h),green,.006)
 box('GC_Leaf_lower_panel',(xc,-3.16,.49),(.47,.044,.77),green,.006)
 for face in [-1,1]:
  y=-3.16+face*.027
  box('GC_Leaf_kick_plate',(xc,y,.25),(.438,.004,.27),metal,.005)
  for x in [xc-.19,xc+.19]:
   for z in [.135,.365]:screw(x,y+face*.004,z,face<0)
 for x in [sign*.079,sign*.535]:box('GC_Glass_vertical_gasket',(x,-3.16,1.487),(.014,.032,1.025),rubber,.003)
 for z in [.978,1.995]:box('GC_Glass_horizontal_gasket',(xc,-3.16,z),(.442,.032,.014),rubber,.003)
 box('GC_Leaf_glass',(xc,-3.16,1.487),(.442,.009,1.002),glass,.002)
 box('GC_Soft_meeting_edge',(sign*.008,-3.16,1.047),(.016,.056,2.054),rubber,.005)
 box('GC_Replaceable_sweep',(xc,-3.16,.021),(.585,.044,.016),rubber,.003)
 text('GC_Door_arrow','<  SLIDE' if sign<0 else 'SLIDE  >',(xc,-3.198,.825),.038,ink)
 for x in [xc-.15,xc+.15]:
  box('GC_Roller_carriage',(x,-3.14,2.13),(.084,.018,.078),metal,.004)
  for z in [2.145,2.225]:
   rr=empty('GC_ROLLER',(x,-3.177,z));o=cyl('GC_Track_roller',(x,-3.177,z),.026,.018,rubber,'Y',32);parent_keep(o,rr);o=cyl('GC_Roller_hub',(x,-3.188,z),.010,.008,metal,'Y',24);parent_keep(o,rr);parent_keep(rr,root);rollers.append((rr,sign))
  screw(x,-3.165,2.11)
 box('GC_Rack',(-sign*.05,-3.125,2.185+sign*.035),(1.30,.025,.011),metal,.001)
 for j in range(65):box('GC_Rack_tooth',(-sign*.05-.64+j*.020,-3.125,2.185+sign*.026),(.010,.022,.009),metal,.001)
 for o in list(collection.objects):
  if not o.parent:parent_keep(o,root)
group=interior
# Clear central aisle: durable floor, individual pads and serviceable under-seat heaters.
box('GC_Floor_finish',(0,0,.005),(2.97,5.91,.010),dark,.001)
for y in [i*.12-2.76 for i in range(47)]:box('GC_Floor_rib',(0,y,.011),(2.93,.008,.004),rubber,.001)
for x in [-.59,.59]:box('GC_Threshold_warning',(x,-2.86,.012),(.025,.20,.006),amber,.001)
for sign in [-1,1]:
 for y in [-1.55,-.05,1.45]:
  box('GC_Shaped_seat_pad',(sign*1.25,y,.51),(.42,1.40,.085),vinyl,.034)
  box('GC_Padded_backrest',(sign*1.455,y,.75),(.085,1.40,.34),vinyl,.027)
  points=[(sign*1.25-.18,y-.65,.548),(sign*1.25+.18,y-.65,.548),(sign*1.25+.18,y+.65,.548),(sign*1.25-.18,y+.65,.548),(sign*1.25-.18,y-.65,.548)]
  tube('GC_Cushion_piping',points,.004,rubber)
  box('GC_Seat_pedestal_face',(sign*1.043,y,.25),(.018,1.30,.32),cream,.005)
  for j in range(12):box('GC_Heater_vent',(sign*1.031,y-.53+j*.095,.21),(.004,.057,.012),dark,.001)
  for z in [.13,.36]:
   for dy in [-.57,.57]:cyl('GC_Seat_panel_screw',(sign*1.030,y+dy,z),.006,.004,metal,'X',16)
 for y in [-2.48,2.25]:
  rod('GC_Grab_rail_support',(sign*1.25,y,1.95),(sign*1.47,y,1.95),.018,metal)
 for y in [-2.46]:
  rod('GC_Boarding_stanchion',(sign*.94,y,.065),(sign*.94,y,2.19),.021,amber)
  for z in [.055,2.19]:cyl('GC_Stanchion_socket',(sign*.94,y,z),.046,.035,metal)
 # Low brass luggage hooks stay over seats rather than in the central aisle.
 for y in [-1.9,-.8,.3,1.4]:tube('GC_Coat_hook',[(sign*1.46,y,1.06),(sign*1.37,y,1.06),(sign*1.37,y,1.10)],.006,metal)
box('GC_Rear_route_board',(0,2.905,.68),(1.12,.012,.30),cream,.006)
text('GC_Route_title','MILLFORD  —  MALDEK',(0,2.895,.735),.058,dark)
text('GC_Route_sub','01     /     MOUNTAIN SERVICE     /     1991',(0,2.895,.615),.028,dark)
box('GC_Emergency_housing',(1.21,-2.91,1.28),(.28,.07,.30),cream,.015)
text('GC_Emergency_label','ASSISTANCE',(1.21,-2.87,1.385),.034,dark,True)
cyl('GC_Call_button',(1.21,-2.855,1.27),.031,.024,red,'Y',32)
for x in [1.13,1.17,1.21,1.25,1.29]:box('GC_Speaker_slot',(x,-2.869,1.185),(.012,.006,.036),dark,.003)
box('GC_Release_box',(-1.20,-2.91,1.38),(.30,.05,.15),red,.006)
text('GC_Release_label','EMERGENCY RELEASE',(-1.20,-2.88,1.41),.025,ink,True)
rod('GC_Release_handle',(-1.30,-2.86,1.345),(-1.10,-2.86,1.345),.009,metal)
text('GC_Capacity','8 PERSONS  /  640 kg',(-1.20,-2.88,1.12),.032,ink,True)
# Retain the two original ceiling lamp surfaces; add protective housings, not brighter emission.
for y in [-1.65,1.55]:
 for x in [-.44,.44]:box('GC_Lamp_endcap',(x,y,2.26),(.05,.22,.055),cream,.012)
 for yy in [y-.105,y+.105]:box('GC_Lamp_guard',(0,yy,2.257),(.83,.012,.052),metal,.003)
for x in [-1.38,1.38]:rod('GC_Ceiling_conduit',(x,-2.75,2.23),(x,2.74,2.23),.008,metal)
random.seed(91)
for i in range(32):
 x=random.choice([-.57,.57])+random.uniform(-.008,.008);z=random.uniform(.05,.85);group=left if x<0 else right;o=box('GC_Local_edge_wear',(x,-3.196,z),(.007,.0006,random.uniform(.006,.025)),metal,.001);parent_keep(o,roots[0 if x<0 else 1])
# Review cycle: cabin arrives closed, settles, opens, dwells, closes, then departs.
s.render.fps=24;s.frame_end=384
keys=[(1,0),(60,0),(78,0),(162,1),(264,1),(306,0),(348,0),(384,0)]
for root,sign in zip(roots,[-1,1]):
 for f,q in keys:root.location.x=sign*.635*q;root.keyframe_insert(data_path='location',frame=f)
for rr,sign in rollers:
 for f,q in keys:rr.rotation_euler.y=-sign*.635*q/.026;rr.keyframe_insert(data_path='rotation_euler',frame=f)
for f,q in keys:pinion.rotation_euler.y=.635*q/.034;pinion.keyframe_insert(data_path='rotation_euler',frame=f)
for f,name in [(1,'APPROACH / DOORS LOCKED'),(60,'CABIN STOPPED'),(78,'SETTLED / OPEN SOUND'),(162,'BOARDING'),(240,'CLOSING WARNING'),(264,'CLOSE SOUND'),(306,'CLOSED / LATCH'),(348,'DEPARTURE RELEASED')]:s.timeline_markers.new(name,frame=f)
cabinroot=empty('GC_CABIN_APPROACH_ROOT',(0,0,0))
for o in list(s.objects):
 if o!=cabinroot and not o.parent:parent_keep(o,cabinroot)
for f,y in [(1,6),(60,0),(348,0),(384,6)]:cabinroot.location.y=y;cabinroot.keyframe_insert(data_path='location',frame=f)
seq=s.sequence_editor_create()
for name,frame in [('Gondola_Door_Open',78),('Gondola_Door_Close',264)]:
 strip=seq.strips.new_sound(name,str(REPO/'art/audio/gondola_doors/wav'/(name+'.wav')),channel=1,frame_start=frame);strip.volume=.8
group=studio
floor=box('Review_ground',(0,0,-.33),(200,200,.10),mat('GC01_Studio_floor',(.026,.038,.036),0,.8),.0)
for name,p,energy,size in [('Key',(3,-6,7),1500,5),('Fill',(-5,-2,4),900,5),('Rim',(0,7,6),1800,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,p,target,lens):
 data=bpy.data.cameras.new(name);data.lens=lens;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cameras=[camera('01_Cabin_exterior',(7,-11,5.6),(0,0,1.8),48),camera('02_Door_detail',(2.75,-7,2.7),(0,-3.12,1.18),62),camera('03_Interior',(0,-2.65,1.60),(0,2.6,1.22),22),camera('04_Track_detail',(1.7,-5.4,2.90),(0,-3.15,2.18),75),camera('05_Inside_doors',(1.0,-.30,1.60),(0,-3.1,1.26),30)]
s.world=bpy.data.worlds.new('GC01_Review_world');s.world.color=(.18,.18,.18)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.frame_set(1);s.camera=cameras[0]
runpy.run_path(str(OUT/'scripts/refine_fittings.py'),run_name='gondola_refinements')['refine']()
for a in bpy.data.screens:
 for area in a.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=500
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Gondola_Cabin.blend'))
manifest={'scope':'Blender design and sourced sounds for review; not installed in Unreal','source':'visual_fidelity_07/Maldek_Station_Cleanup.blend','origin_shift_m':[0,8.05,4],'removed_replaced_objects':removed,'doorway_clear_m':[1.20,2.10],'leaf_travel_m':.635,'door_plane_y_m':-3.16,'opening_seconds':3.5,'closing_seconds':1.75,'settle_seconds':.75,'fps':24,'frames':dict((n,f) for f,n in [(60,'stopped'),(78,'open_start'),(162,'open'),(264,'close_start'),(306,'closed'),(348,'departure')]),'integration_rule':'Stopped cabin and deployed landing before opening; doorway obstruction reopens/holds; closed latch before gangway retraction and route movement; preserve existing dim lamps.'}
(OUT/'design_manifest.json').write_text(json.dumps(manifest,indent=2))
for name,cam,f in [('01_Closed',cameras[0],60),('02_Open',cameras[0],180),('03_Door_detail',cameras[1],60),('04_Interior',cameras[2],180),('05_Track',cameras[3],112),('06_Inside_doors',cameras[4],60)]:
 s.frame_set(f);s.camera=cam;cover.hide_render=name=='05_Track';bpy.data.objects['GC_Guard_plate'].hide_render=name=='05_Track';s.render.filepath=str(OUT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
cover.hide_render=False;bpy.data.objects['GC_Guard_plate'].hide_render=False;s.frame_set(180);s.camera=cameras[0];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Gondola_Cabin.blend'))
