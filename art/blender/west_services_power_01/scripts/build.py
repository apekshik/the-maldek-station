import bpy, math, json, hashlib, bmesh
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]; O=Vector((-37.45,-5,1.2)); SRC=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend'
bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene; s.name='WSE_Asset_Source'; s.unit_settings.system='METRIC'
c=bpy.data.collections.new('WSE_ASSETS');s.collection.children.link(c)
def mat(n,col,metal=0):
 m=bpy.data.materials.new('WSE_'+n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.43
 return m
pet=mat('Petrol_enamel',(.035,.19,.17),.35); steel=mat('Galvanized',(.45,.5,.49),.75);rub=mat('Rubber',(.023,.029,.026));cream=mat('Cream',(.78,.74,.58));black=mat('Ink',(.018,.025,.022));red=mat('Red',(.55,.04,.018));yellow=mat('Safety_ochre',(.85,.5,.08));green=mat('Run',(.025,.15,.04));startgreen=mat('Start_green',(.08,.5,.14));oil=mat('Contact_darkening',(.085,.075,.045))
def own(o,n,m):
 o.name='WSE_'+n
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def box(n,p,d,m=pet,b=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=own(bpy.context.object,n,m);o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:mod=o.modifiers.new('Machined edges','BEVEL');mod.width=min(b,min(d)*.2);mod.segments=2
 return o
def cyl(n,a,b,r,m=steel,verts=24):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2);o=own(bpy.context.object,n,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def tube(n,pts,r,m=steel,wall=.012):
 # connected hollow swept ring mesh, annular ends
 rounded=[Vector(pts[0])]
 for i in range(1,len(pts)-1):
  a,q,b=map(Vector,pts[i-1:i+2]);rr=min(.15,(q-a).length*.25,(b-q).length*.25);aa=q+(a-q).normalized()*rr;bb=q+(b-q).normalized()*rr
  for j in range(7):
   f=j/6;rounded.append((1-f)**2*aa+2*f*(1-f)*q+f*f*bb)
 rounded.append(Vector(pts[-1]));pts=rounded
 vs=[];N=24;prev=None
 for k,p in enumerate(pts):
  p=Vector(p);t=Vector(pts[min(k+1,len(pts)-1)])-Vector(pts[max(0,k-1)]);t.normalize();u=t.cross(Vector((0,0,1)))
  if u.length<.01:u=t.cross(Vector((0,1,0)))
  if prev is not None:u=prev-t*prev.dot(t)
  u.normalize();prev=u.copy();v=t.cross(u)
  for rr in [r,r-wall]:
   vs.extend([p+rr*(math.cos(i*math.tau/N)*u+math.sin(i*math.tau/N)*v) for i in range(N)])
 fs=[]
 for k in range(len(pts)-1):
  for q in [0,1]:
   for i in range(N):
    a=k*2*N+q*N+i;bb=k*2*N+q*N+(i+1)%N;f=(a,bb,bb+2*N,a+2*N);fs.append(f if q==0 else f[::-1])
 for k in [0,len(pts)-1]:
  for i in range(N):
   a=k*2*N+i;bb=k*2*N+(i+1)%N;f=(a,a+N,bb+N,bb);fs.append(f if k==0 else f[::-1])
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('WSE_'+n,me);c.objects.link(o);me.materials.append(m);return o
def text(n,body,p,size=.07,rot=(math.pi/2,0,0),m=cream):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.extrude=.0005;o=bpy.data.objects.new('WSE_'+n,cu);c.objects.link(o);o.location=p;o.rotation_euler=rot;cu.materials.append(m);return o
def empty(n,p):
 o=bpy.data.objects.new(n,None);c.objects.link(o);o.location=p;o.empty_display_type='ARROWS';o.empty_display_size=.12;return o
def parent(o,p):
 w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
moving=[]
def pivot(n,p,objs,angle):
 e=empty('WSE_'+n,p);bpy.context.view_layer.update()
 for o in objs:parent(o,e)
 moving.append((e,angle));return e
# compact set: 2.50 x 1.30 m reservation
box('Drain_pan',(2.9,2.85,.08),(2.5,1.3,.09),oil)
for x in [1.86,3.94]:
 for y in [2.35,3.35]:
  cyl('Vibration_foot',(x,y,.125),(x,y,.23),.09,rub);box('Mount_plate',(x,y,.23),(.23,.22,.03),steel)
for y in [2.3,3.4]:box('Skid_rail',(2.9,y,.32),(2.5,.12,.15),steel)
box('Integral_day_tank',(2.9,2.85,.43),(1.75,.82,.18),pet)
box('Crankcase',(2.7,2.85,.76),(1.08,.65,.48),pet,.045)
box('Cylinder_head',(2.6,2.85,1.05),(.94,.55,.24),pet,.04)
box('Rocker_cover',(2.6,2.85,1.23),(.97,.49,.13),steel,.04)
for x in [2.25,2.48,2.71,2.94]:
 cyl('Injector',(x,2.62,1.12),(x,2.58,1.23),.022,steel)
 tube('Injector_line',[(x,2.58,1.23),(x,2.48,1.18),(x,2.48,.9)],.013,steel,.004)
cyl('Alternator',(3.22,2.85,.86),(3.95,2.85,.86),.37,pet)
for x in [3.3,3.4,3.5,3.6,3.7,3.8]:tube('Alternator_cooling_ring',[(x,2.85,.86),(x+.022,2.85,.86)],.383,steel,.012)
box('Alternator_terminal',(3.64,2.85,1.27),(.38,.34,.15),pet)
box('Radiator_housing',(1.91,2.85,.91),(.25,1.04,1.08),pet)
for y in [2.4+i*.05 for i in range(19)]:box('Radiator_fin',(1.773,y,.91),(.025,.016,.91),steel,.001)
# guard is opaque formed removable cover
box('Belt_guard',(2.17,2.5,.91),(.18,.10,.68),yellow,.03)
for x in [2.47,2.8]:cyl('Spin_on_filter',(x,2.37,.65),(x,2.37,.93),.075,cream)
cyl('Starter',(3.04,2.48,.66),(3.3,2.48,.66),.09,black)
tube('Coolant_hose',[(2.18,2.9,1.22),(2.1,3.16,1.23),(1.94,3.16,1.28)],.044,rub,.008)
cover=box('Service_cover',(2.66,3.193,.83),(.78,.026,.3),pet)
ec=pivot('Engine_cover_hinge',(2.66,3.21,.99),[cover],math.radians(100));ec['open_axis']='X'
for x in [2.3,3.02]:
 for z in [.69,.96]:cyl('Cover_fastener',(x,3.207,z),(x,3.217,z),.017,steel,6)
# operator controls on north-facing separate pedestal
box('Panel_pedestal',(3.45,3.35,.73),(.12,.12,1.2),steel)
box('Control_box',(3.45,3.39,1.46),(1.12,.24,.72),pet)
# text normal +Y
rot=(math.pi/2,0,math.pi)
text('Panel_title','STANDBY / AUXILIARY',(3.96,3.518,1.735),.07,rot)
for x,lab in [(3.72,'VOLTS'),(3.2,'Hz')]:
 cyl('Meter_bezel',(x,3.515,1.55),(x,3.545,1.55),.133,steel)
 cyl('Meter_face',(x,3.546,1.55),(x,3.55,1.55),.115,cream)
 for i in range(9):
  a=math.radians(25+i*16);xx=x+math.cos(a)*.086;zz=1.55+math.sin(a)*.086;box('Meter_tick',(xx,3.553,zz),(.008,.005,.019),black,.001)
 needle=box('Needle',(x,3.557,1.57),(.006,.005,.09),black,.001);needle.rotation_euler[1]=-.7
 text('Meter_units',lab,(x+.072,3.562,1.48),.039,rot,black)
for x,lab,m in [(3.85,'START',startgreen),(3.62,'STOP',black),(3.39,'FAULT',red),(3.15,'RUN',green)]:
 cyl(lab+'_button' if lab in ['START','STOP'] else lab+'_lens',(x,3.515,1.27),(x,3.553,1.27),.035,m);text(lab+'_label',lab,(x+.075,3.563,1.18),.034,rot)
box('Stop_backplate',(2.94,3.524,1.55),(.14,.02,.19),yellow)
cyl('Emergency_stop',(2.94,3.54,1.55),(2.94,3.62,1.55),.055,red)
# north-wall battery box open construction
for p,d in [((3.6,9.12,.12),(1.2,.64,.08)),((3.6,8.81,.52),(1.2,.04,.72)),((3.02,9.12,.52),(.04,.6,.72)),((4.18,9.12,.52),(.04,.6,.72))]:box('Battery_case',p,d,pet)
for x in [3.32,3.86]:
 box('Battery',(x,9.15,.4),(.43,.42,.46),black)
 box('Hold_down',(x,9.15,.647),(.045,.46,.025),steel)
 for y,m in [(9.0,red),(9.3,black)]:box('Protected_terminal',(x+.11,y,.66),(.075,.065,.045),m)
lid=box('Battery_lid',(3.6,9.12,.91),(1.22,.65,.045),pet)
e=pivot('Battery_lid_hinge',(3.6,8.80,.91),[lid],0);e['open_axis']='X';moving[-1]=(e,math.radians(100))
# relocate battery assembly beside alternator; preserve hierarchy exactly once
bpy.context.view_layer.update()
for ob in list(c.objects):
 if ob.name.startswith(('WSE_Battery','WSE_Hold_down','WSE_Protected_terminal')) and ob.parent is None:ob.location+=Vector((1.3,-6.1,0))
tube('Battery_DC',[(5.28,3.2,.67),(5.35,3.35,.67),(4.3,3.35,.5),(4.0,3.03,.5),(3.24,3.03,.64)],.018,rub,.006)
tube('Battery_positive',[(4.73,2.9,.68),(4.6,2.65,.69),(4.2,2.65,.5),(3.24,3.10,.64)],.016,red,.005)
tube('Battery_series_link',[(4.73,3.2,.68),(4.95,3.2,.75),(5.27,2.9,.68)],.016,rub,.005)
# distribution cabinet facing west (text normal -X)
rwest=(math.pi/2,0,-math.pi/2)
for p,d in [((5.53,7,1.25),(.04,1.62,1.52)),((5.35,6.17,1.25),(.36,.04,1.6)),((5.35,7.83,1.25),(.36,.04,1.6)),((5.35,7,2.03),(.36,1.62,.04)),((5.35,7,.47),(.36,1.62,.04))]:box('Distribution_case',p,d,pet)
for y,lab in [(6.43,'01 LIGHTING'),(7,'02 RADIO'),(7.57,'03 RESCUE HEAT')]:
 box('Breaker',(5.38,y,1.4),(.13,.32,.32),black)
 lever=box('Breaker_handle',(5.29,y,1.4),(.07,.12,.04),cream);pivot('Breaker_'+lab,(5.31,y,1.4),[lever],.5)
 text('Circuit_'+lab,lab,(5.505,y+.22,1.66),.045,rwest)
 cx=5.32+(y-6.43)*.12
 tube('Circuit_conduit',[(cx,y,2.04),(cx,y,2.8),(cx,9.4,2.8)],.021,steel,.006)
door=box('Distribution_door',(5.147,7,1.25),(.04,1.61,1.51),pet)
mark=text('Distribution_mark','EMERGENCY SUPPLY\nLIGHT / RADIO / HEAT\nNO GONDOLA DRIVE',(5.12,7.6,1.57),.078,rwest)
pivot('Distribution_hinge',(5.12,7.81,1.25),[door,mark],math.radians(-110))
box('Transfer_box',(5.4,5.48,1.48),(.32,.65,.65),cream)
text('Transfer_states','NORMAL   OFF   EMERGENCY',(5.23,5.75,1.68),.039,rwest,black)
selector=box('Transfer_handle',(5.19,5.48,1.48),(.1,.04,.24),black);pivot('Transfer_selector',(5.19,5.48,1.48),[selector],0)
text('Transfer_rule','AUXILIARY ONLY',(5.23,5.72,1.25),.052,rwest,black)
tube('AC_feed',[(3.7,2.85,1.28),(3.7,2.85,2.75),(5.42,2.85,2.75),(5.42,5.14,2.75),(5.42,5.14,1.4)],.032,rub,.01)
# fuel service on accessible north edge
cyl('Fuel_level_bezel',(2.25,3.31,.55),(2.25,3.36,.55),.075,steel)
cyl('Fuel_level_face',(2.25,3.365,.55),(2.25,3.37,.55),.06,cream)
text('Fuel_level','1/2',(2.29,3.378,.535),.031,rot,black)
tube('Fuel_supply',[(2.35,3.15,.44),(2.35,3.36,.62),(2.65,3.36,.62),(2.65,3.12,.86)],.013,steel,.004)
valve=box('Fuel_isolation_lever',(2.44,3.39,.65),(.18,.025,.025),red);pivot('Fuel_valve',(2.35,3.39,.65),[valve],math.pi/2)
text('Emergency_stop_label','EMERGENCY STOP',(3.06,3.565,1.38),.026,rot,black)
text('Fuel_identification','FUEL / ISOLATE',(2.95,3.279,.43),.042,rot)
# frames fit rough opening leaving concealed separation, no shared shell recess necessary
for y in [6.445,7.955]:box('Door_jamb',(.12,y,1.15),(.31,.08,2.29),steel,.005)
box('Door_header',(.12,7.2,2.255),(.31,1.43,.09),steel,.005)
box('Threshold',(.12,7.2,.013),(.31,1.43,.016),steel,.003)
for yy in [6.455,7.945]:box('Door_seal',(.2875,yy,1.12),(.025,.07,2.175),rub,.002)
box('Door_head_seal',(.2875,7.2,2.208),(.025,1.42,.018),rub,.002)
for y,hinge,angle in [(6.835,6.49,-math.pi/2),(7.565,7.91,math.pi/2)]:
 leaf=box('Service_door',(.33,y,1.12),(.06,.71,2.17),pet,.012)
 handle=box('Door_pull',(.38,7.13 if y<7.2 else 7.27,1.06),(.07,.03,.2),steel)
 dp=pivot('Door_hinge_S' if y<7.2 else 'Door_hinge_N',(.30,hinge,1.12),[leaf,handle],angle)
 lock=cyl('Door_lock',(.37,7.13 if y<7.2 else 7.27,.92),(.39,7.13 if y<7.2 else 7.27,.92),.026,steel);bpy.context.view_layer.update();parent(lock,dp)
 ext=box('Exterior_push_plate',(.303,7.13 if y<7.2 else 7.27,1.06),(.014,.065,.19),steel);sweep=box('Door_bottom_seal',(.33,y,.029),(.045,.71,.02),rub,.002);bpy.context.view_layer.update();parent(ext,dp);parent(sweep,dp)
 for z in [.32,1.12,1.96]:cyl('Hinge_barrel',(.30,hinge,z-.055),(.30,hinge,z+.055),.022,steel)
text('Entrance_sign','EMERGENCY POWER\nAUXILIARY SUPPLY ONLY',(-.047,7.9,2.7),.09,rwest)
# louvres, south opening discharge / north opening intake
for yc,zc,name in [(1.95,1.15,'DISCHARGE'),(4.95,1.65,'INTAKE')]:
 for y in [yc-.71,yc+.71]:box(name+'_jamb',(.12,y,zc),(.31,.06,1.08),steel,.003)
 for z in [zc-.51,zc+.51]:box(name+'_rail',(.12,yc,z),(.31,1.36,.06),steel,.003)
 for i in range(8):
  blade=box(name+'_blade',(.11,yc,zc-.42+i*.12),(.23,1.34,.022),steel,.003);blade.rotation_euler[1]=math.radians(32)
 text(name+'_label',name,(-.055,yc-.5,zc+.65),.09,rwest)
# sealed tapered sheet duct with open ends, four distinct side owners
# x stations with y/z centres and aperture width/height
stations=[(1.775,2.85,.91,1.04,1.08),(.7,2.4,1.15,1.36,.96),(.27,1.95,1.15,1.36,.96),(-.65,1.95,1.15,1.36,.96)]
# One continuous hollow duct; shared corner vertices, no competing sheet skins.
vs=[];fs=[]
for x,y,z,w,h in stations:
 w-=.04;h-=.04
 for ww,hh in [(w+.03,h+.03),(w,h)]:
  vs.extend([(x,y-ww/2,z-hh/2),(x,y+ww/2,z-hh/2),(x,y+ww/2,z+hh/2),(x,y-ww/2,z+hh/2)])
for k in range(len(stations)-1):
 for q in [0,1]:
  for i in range(4):
   a=k*8+q*4+i;b=k*8+q*4+(i+1)%4;f=(a,b,b+8,a+8);fs.append(f if q==0 else f[::-1])
for k in [0,len(stations)-1]:
 for i in range(4):
  a=k*8+i;b=k*8+(i+1)%4;f=(a,a+4,b+4,b);fs.append(f if k==0 else f[::-1])
me=bpy.data.meshes.new('Continuous duct');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('WSE_Discharge_duct',me);c.objects.link(ob);me.materials.append(steel);me.materials.append(rub)
for f in me.polygons:
 if f.index<8:f.material_index=1
# exterior separator between louvres, restrict immediate lateral mixing
box('Air_separator',(-.36,3.0,1.4),(.92,.035,1.9),steel)
# insulated exhaust continuous centerline and open bore
route=[(2.25,2.7,1.23),(2.25,2.7,1.65),(2.25,2.5,1.95),(2.25,.55,1.95),(2.25,-.3,1.95),(2.25,-.3,7.55)]
tube('Exhaust_insulated_route',route,.095,steel,.037)
for z in [1.31+i*.04 for i in range(7)]:tube('Flexible_bellows',[(2.25,2.7,z),(2.25,2.7,z+.016)],.11,steel,.012)
tube('Silencer',[(2.25,1.8,1.95),(2.25,.85,1.95)],.20,steel,.05)
# tapered silencer end closures meet the insulated pipe, with a separate outer owner
for ya,yb,ra,rb in [(1.8,1.9,.20,.096),(.85,.75,.20,.096)]:
 bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=ra,radius2=rb,depth=abs(yb-ya),location=(2.25,(ya+yb)/2,1.95));ob=own(bpy.context.object,'Silencer_end_reducer',steel);ob.rotation_euler[0]=-math.pi/2 if yb>ya else math.pi/2
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();mod=ob.modifiers.new('Reducer wall','SOLIDIFY');mod.thickness=.012
# sleeve through south shell, exact patch generated in review builder
tube('Wall_sleeve',[(2.25,-.06,1.95),(2.25,.31,1.95)],.15,steel,.018)
tube('Sleeve_annular_seal',[(2.25,-.045,1.95),(2.25,.295,1.95)],.131,rub,.035)
for z in [2.35,3.45,4.7,6.1,7.0]:
 tube('Riser_clamp',[(2.25,-.3,z-.025),(2.25,-.3,z+.025)],.11,steel,.01)
 box('Riser_standoff',(2.25,-.12,z),(.04,.3,.035),steel)
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.21,radius2=.025,depth=.13,location=(2.25,-.3,7.66));own(bpy.context.object,'Weather_cap',steel)
for x in [2.13,2.37]:box('Cap_support',(x,-.3,7.54),(.015,.015,.16),steel)
for n,p in {'START':(3.85,3.62,1.27),'TRANSFER':(5.13,5.48,1.48),'FUEL_ISOLATE':(2.44,3.47,.65),'FUEL_CHECK':(2.25,3.45,.55),'BATTERY_SERVICE':(4.9,3.65,.9),'EMERGENCY_STOP':(2.94,3.67,1.55),'STATUS_READ':(3.45,3.75,1.55)}.items():empty('WSE_'+n,p)
empty('WSE_ORIENTATION_PLUS_Y',(0,1,0));empty('WSE_ORIENTATION_EAST',(2,0,0))
# usable local UVs on every mesh, retain modifiers and parts
for o in list(c.objects):
 if o.type=='MESH':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.03);bpy.ops.object.mode_set(mode='OBJECT')
# mesh labels are separate editable fonts; export conversion deferred
bpy.context.view_layer.update()
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
mechanisms=[]
for e,angle in moving:
 axis=0 if e.get('open_axis')=='X' or 'Transfer_selector' in e.name or 'Breaker_' in e.name else (1 if 'Fuel_valve' in e.name else 2)
 closed={o.name:bounds(o) for o in e.children};sweep=[]
 for i in range(19):
  e.rotation_euler[axis]=angle*i/18;bpy.context.view_layer.update();sweep.extend([v for o in e.children for v in bounds(o)])
 e.rotation_euler[axis]=0;bpy.context.view_layer.update()
 mechanisms.append({'pivot':e.name,'local_position':list(e.location),'axis':'XYZ'[axis],'closed_degrees':0,'open_degrees':math.degrees(angle),'swept_bounds':[[min(v[i] for v in sweep) for i in range(3)],[max(v[i] for v in sweep) for i in range(3)]]})
manifest={'collection':'WSE_ASSETS','units':'metres','origin_world':list(O),'matrix_local_to_world':[list(r) for r in Matrix.Translation(O)],'orientation_markers':{'WSE_ORIENTATION_PLUS_Y':[0,1,0],'WSE_ORIENTATION_EAST':[2,0,0]},'replace_collection':'WS_POWER_PROXY','remove_objects':[],'mechanisms':mechanisms,'anchors':{o.name:list(o.location) for o in c.objects if o.type=='EMPTY' and o.name in ['WSE_'+n for n in ['START','TRANSFER','FUEL_ISOLATE','FUEL_CHECK','BATTERY_SERVICE','EMERGENCY_STOP','STATUS_READ']]},'objects':{o.name:{'type':o.type,'bounds':bounds(o) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []} for o in c.objects},'export':'Only WSE_ASSETS. No scale conversion yet; no FBX/runtime collision delivered. Smart UVs per part; atlas baking and LOD pending.'}
with bpy.data.libraries.load(str(SRC),link=False) as (a,b):b.collections=['WS_POWER_PROXY']
proxy=b.collections[0];manifest['remove_objects']=[o.name for o in proxy.all_objects]
for o in list(proxy.all_objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(proxy)
(P/'assembly.json').write_text(json.dumps(manifest,indent=2))
s['review_states']='Stopped default; running indication only in review builder; no runtime behavior'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Emergency_Power.blend'))
print('ASSET SAVED',len(c.objects))











