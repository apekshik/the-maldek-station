"""VF08 generator and horizontal diesel tank study. Writes only this revision."""
import bpy,math,json,ast,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/apek-anna/Developer/the-maldek-station');OUT=Path(__file__).resolve().parents[1]
SOURCE=OUT.parent/'visual_fidelity_07/Maldek_Station_Cleanup.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
steel=bpy.data.materials['VF06_Structural_steel'];blue=bpy.data.materials['VF06_Petrol_paint'];zinc=bpy.data.materials['VF06_Galvanized'];cream=bpy.data.materials['VF06_Warm_enamel']
for rel,names in [('visual_fidelity_01/scripts/build_sample.py',['mesh','box','beam','bolt','material','panel','area','camera']),('visual_fidelity_02/scripts/build_redesign.py',['cylinder']),('visual_fidelity_06/scripts/build_integrated.py',['bounds','col','pipe','sign'])]:
 for n in ast.parse((OUT.parent/rel).read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module(body=[n],type_ignores=[]),rel,'exec'))
steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized'];blue=bpy.data.materials['VF06_Petrol_paint'];green=bpy.data.materials['VF06_Service_green'];concrete=bpy.data.materials['VF06_Concrete'];cream=bpy.data.materials['VF06_Warm_enamel'];yellow=bpy.data.materials['VF06_Safety_ochre'];rust=bpy.data.materials['VF06_Fastener_oxidation'];rubber=bpy.data.materials['VF06_Rubber'];lamp=bpy.data.materials['VF06_Lamp']
red=material('VF08_Oxide_Red',(.3,.048,.025),.3,.52)
# Scoped replacement of remote equipment and shells; relay and water infrastructure remain.
deleted=[]
for cn in ['21_Maintenance','VF06_Maintenance_Shells','VF06_Service_Hardware']:
 for o in list(bpy.data.collections[cn].objects):
  if cn=='21_Maintenance' or (((bounds(o)[0]+bounds(o)[1])/2).x<43 and ((bounds(o)[0]+bounds(o)[1])/2).y<0):
   deleted.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 if o.type=='FONT' and o.data.body=='GENERATOR':deleted.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
original={o.name:[list(v) for v in bounds(o)] for o in bpy.data.objects if o.type=='MESH'}
# Helpers use world metre coordinates; machine parts use the hall southwest floor datum.
def B(n,p,d,m=steel,b=.006):return box('VF08_'+n,p,d,m,b)
def C(n,p,r,h,m=zinc,axis='Z',v=32):return cylinder('VF08_'+n,p,r,h,m,axis,v)
def P(n,points,r=.03,m=zinc):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for a,p in zip(sp.points,points):a.co=(*p,1)
 o=bpy.data.objects.new('VF08_'+n,cu);group.objects.link(o);cu.materials.append(m);return o

def ring(n,p,r,t,m=zinc,axis='X'):
 # Continuous annulus, not a filled cylinder covering the tank shell.
 vs=[];faces=[];N=64
 for z in [-t/2,t/2]:
  for rr in [r-.012,r+.012]:
   for i in range(N):vs.append((rr*math.cos(i*2*math.pi/N),rr*math.sin(i*2*math.pi/N),z))
 for i in range(N):
  j=(i+1)%N
  for a,b in [(0,N),(N,3*N),(3*N,2*N),(2*N,0)]:faces.append((a+i,a+j,b+j,b+i))
 o=mesh('VF08_'+n,vs,faces,m);o.location=p
 if axis=='X':o.rotation_euler.y=math.pi/2
 if axis=='Y':o.rotation_euler.x=math.pi/2
 return o

def label(txt,p,size=.13,rot=(math.pi/2,0,0),mat=cream):return sign(txt,p,size,rot,mat)
def flange(n,p,r=.09,axis='Z'):
 C(n,p,r,.035,zinc,axis)
 for i in range(8):
  a=i*math.pi/4;v=(r*.76*math.cos(a),r*.76*math.sin(a))
  q=(p[0]+v[0],p[1]+v[1],p[2]+.025) if axis=='Z' else ((p[0]+.025,p[1]+v[0],p[2]+v[1]) if axis=='X' else (p[0]+v[0],p[1]-.025,p[2]+v[1]))
  C('Flange_fastener',q,.009,.016,steel,axis,6)

def wall(axis,fixed,lo,hi,ops,z=-1,h=4.4):
 start=set(group.objects);edges=sorted(set([lo,hi]+[u for a,b,c,d in ops for u in (a,b)]))
 def pt(u,v,k):return (u,v,k) if axis=='X' else (v,u,k)
 def dim(u,v,k):return (u,v,k) if axis=='X' else (v,u,k)
 outward=1 if fixed in [-9,37,41] else -1
 for a,b in zip(edges,edges[1:]):
  op=next((q for q in ops if q[0]<=(a+b)/2<=q[1]),None)
  for low,high in ([(0,h)] if op is None else [(0,op[2]),(op[3],h)]):
   if high-low<.01:continue
   before=set(group.objects);panel(axis,fixed,a+.008,b-.008,z+low+.004,z+high-.004,outward,green)
   for o in set(group.objects)-before:o.name='VF08_'+o.name
 for a,b,c,d in ops:
  for u in [a-.035,b+.035]:B('Opening_jamb',pt(u,fixed,z+(c+d)/2),dim(.07,.31,d-c+.07),steel)
  for k in ([z+c-.035] if c>0 else [])+[z+d+.035]:B('Opening_header',pt((a+b)/2,fixed,k),dim(b-a+.14,.31,.07),steel)
  if c==0:B('Flush_threshold',pt((a+b)/2,fixed,z+.008),dim(b-a,.42,.016),zinc,.002)
 return list(set(group.objects)-start)

def louver(axis,fixed,a,b,z0,z1):
 def pt(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 def dim(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 for k in range(max(2,int((z1-z0)/.11))):
  o=B('Vent_louver',pt((a+b)/2,fixed,z0+.055+k*.11),dim(b-a-.06,.18,.028),zinc,.003)
  if axis=='X':o.rotation_euler.x=.45
  else:o.rotation_euler.y=.45

group=col('VF08_01_Generator_Shell');shell=group
B('Hall_foundation',(32,-14,-1.214),(10.2,10.2,.4),concrete,.02)
# Concrete movement joints are actual seams between shallow finish panels.
for i in range(5):
 for j in range(5):B('Floor_panel',(28+i*2,-18+j*2,-1.006),(1.992,1.992,.012),concrete,.002)
wall('Y',27,-19,-9,[(-15.85,-14.15,0,2.65)])
wall('Y',37,-19,-9,[(-16.3,-14.7,0,2.65),(-11.5,-9.8,.5,3.3)])
louver('Y',37.02,-11.5,-9.8,-.5,2.3)
wall('X',-19,27,37,[(28.7,30.3,0,2.65)])
wall('X',-9,27,37,[(29.9,34.1,.65,3.3)])
louver('X',-8.98,29.9,34.1,-.35,2.3)
for x in [27,32,37]:
 for y in [-19,-9]:
  B('Column',(x,y,1.2),(.19,.19,4.4));B('Column_base',(x,y,-.96),(.4,.4,.08),zinc)
  for dx in [-.14,.14]:
   for dy in [-.14,.14]:bolt((x+dx,y+dy,-.913),'Z')
for y in [-19,-9]:B('Eave_channel',(32,y,3.31),(10.2,.2,.18))
for x in [27,37]:B('Eave_channel',(x,-14,3.31),(.2,10,.18))
# Separate roof collection enables non-destructive cutaway inspection.
group=col('VF08_02_Removable_Roofs');roofs=group
B('Hall_roof',(32,-14,3.49),(10.5,10.5,.18))
for i in range(34):B('Standing_seam',(26.9+i*.31,-14,3.60),(.025,10.42,.03),green,.002)
for y in [-19.23,-8.77]:B('Roof_edge_flashing',(32,y,3.48),(10.5,.06,.30),zinc)
P('Rain_downpipe',[(37.2,-9,3.45),(37.2,-9,-.85),(37.5,-9,-.95)],.045)
# Enlarged workshop retains the old route-facing connection, shifted east with the hall.
group=col('VF08_03_Workshop');workshop=group
B('Workshop_floor',(39,-15,-1.18),(4.2,6.2,.36),concrete)
wall('X',-18,37,41,[],h=3.4);wall('X',-12,37,41,[],h=3.4);wall('Y',41,-18,-12,[],h=3.4)
group=roofs;B('Workshop_roof',(39,-15,2.5),(4.4,6.4,.18))
for i in range(14):B('Workshop_seam',(36.9+i*.31,-15,2.61),(.025,6.35,.03),green,.002)
group=workshop
B('Bench_top',(39.15,-17.35,-.08),(2.9,.78,.09),cream)
for x in [37.85,40.45]:
 for y in [-17.6,-17.1]:B('Bench_leg',(x,y,-.54),(.05,.05,.9))
B('Pegboard',(39.2,-17.83,.9),(2.8,.065,1.1),steel)
for x in [38.2,38.5,38.8,39.1,39.4,39.7,40]:
 C('Tool_handle',(x,-17.91,.9),.016,.32,zinc)
 ring('Tool_ring',(x,-17.92,1.08),.046,.018,zinc,'Y')
for z in [-.5,.2,.9,1.6]:
 B('Storage_shelf',(40.5,-13.6,z),(.7,2.3,.045),zinc)
for y in [-14.7,-12.5]:
 for x in [40.18,40.82]:B('Shelf_upright',(x,y,.5),(.04,.04,2.9))
for y in [-14.3,-13.5]:B('Spare_parts_case',(40.5,y,.4),(.53,.56,.35),green,.02)
# Generator skid, separate engine/alternator/radiator forms, serviceable piping.
group=col('VF08_04_Diesel_Generator');machine=group
B('Inertia_plinth',(32,-13.6,-.93),(2.6,5.6,.14),concrete,.015)
for x in [31.08,32.92]:B('Skid_longitudinal',(x,-13.6,-.70),(.18,5.15,.22))
for y in [-15.65,-14,-11.45]:
 B('Skid_crossmember',(32,y,-.7),(2,.16,.2))
 for x in [31.12,32.88]:
  B('Isolation_rubber',(x,y,-.83),(.28,.28,.1),rubber)
  B('Mount_base',(x,y,-.87),(.37,.35,.035),zinc)
  bolt((x,y,-.84),'Z')
B('Oil_sump',(32,-13.4,-.38),(.9,2.4,.43),green,.05)
B('Crankcase',(32,-13.4,.13),(1.12,2.45,.68),green,.06)
B('Cylinder_head',(32,-13.4,.69),(1.18,2.47,.36),green,.04)
for j in range(6):
 y=-14.38+j*.39
 B('Rocker_cover',(32,y,.96),(.92,.34,.24),green,.06)
 for x in [31.63,32.37]:C('Head_bolt',(x,y,1.092),.023,.02,zinc,'Z',6)
 P('Injector_line',[(31.34,y,.24),(31.27,y,.86),(31.57,y,1.02)],.013,zinc)
B('Intake_manifold',(32.68,-13.4,.72),(.23,2.45,.3),zinc,.06)
P('Exhaust_manifold',[(31.26,-14.5,.76),(31.26,-12.3,.76),(31.16,-12.1,1.15)],.09,steel)
C('Turbocharger',(31.2,-12.05,1.14),.24,.32,steel,'Y',48)
C('Air_cleaner',(32.5,-12.18,1.3),.25,.75,steel,'Y',48)
for y in [-12.45,-11.93]:ring('Airbox_band',(32.5,y,1.3),.252,.045,zinc,'Y')
P('Intake_elbow',[(32.5,-12.55,1.3),(32.65,-12.7,1.2),(32.68,-12.8,.85)],.10,rubber)
C('Alternator_body',(32,-15.32,.27),.62,1.3,green,'Y',64)
for y in [-15.82,-15.5,-15.2,-14.86]:ring('Alternator_cast_rib',(32,y,.27),.631,.06,green,'Y')
C('Alternator_end',(32,-16.02,.27),.57,.10,zinc,'Y',64)
for x in [31.65,31.82,32,32.18,32.35]:B('Alternator_end_vent',(x,-16.083,.27),(.045,.025,.65),steel)
B('Terminal_box',(32,-15.4,1.05),(.7,.6,.38),cream,.025)
P('Power_cable',[(32.3,-15.4,1.12),(33.15,-15.4,1.12),(33.15,-16.5,-.65),(36.5,-16.5,-.65),(36.5,-17.8,.0)],.055,rubber)
B('Radiator_frame',(32,-11.25,.43),(2, .35,2.1),steel,.025)
for x in [31.12+i*.065 for i in range(28)]:B('Radiator_fins',(x,-11.045,.43),(.025,.035,1.9),zinc,.001)
C('Fan_shroud',(32,-11.5,.42),.79,.20,steel,'Y',64)
for i in range(8):
 a=i*math.pi/4;beam('VF08_Fan_guard_spoke',(32,-11.64,.42),(32+.76*math.cos(a),-11.64,.42+.76*math.sin(a)),.018,zinc)
for rr in [.28,.5,.75]:ring('Fan_guard',(32,-11.64,.42),rr,.018,zinc,'Y')
P('Coolant_upper',[(32.7,-12,1.05),(32.72,-11.65,1.2),(32.5,-11.25,1.2)],.065,rubber)
for x in [31.28,31.48]:C('Service_filter',(x,-13.6,-.03),.082,.30,cream)
B('Battery_box',(32.75,-15.75,-.36),(.38,.62,.4),rubber,.03)
label('MALDEK  /  DG-01',(32,-16.14,.32),.11)
# Engine service covers, fasteners and connected exhaust branches.
for j in range(6):
 y=-14.38+j*.39
 B('Crankcase_inspection_cover',(31.427,y,.13),(.03,.30,.32),green,.02)
 for yy in [y-.11,y+.11]:
  for z in [.02,.24]:C('Cover_hex',(31.40,yy,z),.014,.018,zinc,'X',6)
 P('Exhaust_branch',[(31.45,y,.65),(31.27,y,.65),(31.26,y,.76)],.045,steel)
P('Wiring_harness',[(32.48,-14.6,.4),(32.48,-12.2,.4),(32.5,-12.2,1.0)],.018,rubber)
B('Local_control_enclosure',(33.02,-14.4,.66),(.16,.62,.67),cream,.02)
B('Local_control_screen',(33.11,-14.4,.83),(.02,.36,.18),steel)
for y in [-14.58,-14.4,-14.22]:C('Local_control_button',(33.13,y,.53),.026,.025,red if y==-14.58 else zinc,'X')
# Connected plant systems and intentional low-level practical fixtures.
group=col('VF08_05_Plant_Systems');systems=group
P('Exhaust_riser',[(31.16,-12.1,1.15),(30.8,-12.1,1.55),(30.8,-12.1,2.7),(30.8,-10.5,2.7),(30.8,-10.5,4.45)],.10,steel)
C('Exhaust_silencer',(30.8,-11.4,2.7),.25,1.25,zinc,'Y',48)
for y in [-11.93,-10.88]:flange('Silencer_flange',(30.8,y,2.7),.28,'Y')
B('Exhaust_roof_flashing',(30.8,-10.5,3.65),(.65,.65,.08),zinc)
C('Rain_cowl',(30.8,-10.5,4.49),.2,.05,zinc)
for y in [-18,-17.1,-16.2]:
 B('Switchgear_cabinet',(36.52,y,.23),(.68,.76,2.36),cream,.025)
 B('Switchgear_door',(36.16,y,.23),(.04,.69,2.23),green,.015)
 B('Panel_meter',(36.129,y,.90),(.025,.24,.19),steel)
 C('Panel_selector',(36.105,y,.51),.036,.03,zinc,'X')
 label('ISOLATE',(36.09,y,.27),.055,(math.pi/2,0,-math.pi/2))
B('Cable_tray',(35.7,-14,2.45),(.42,8.6,.08),zinc)
for y in [-18,-16,-14,-12,-10]:B('Tray_wall_bracket',(36.35,y,2.4),(1.15,.05,.05))
# Roof-supported hoist crossbeams and bolted hangers.
for y in [-18.1,-10.1]:
 B('Hoist_support_crossbeam',(32,y,3.22),(9.95,.18,.20),steel)
 B('Hoist_hanger',(32,y,3.10),(.20,.24,.24),steel)
 for x in [31.89,32.11]:bolt((x,y,3.24),'Z')
# Hoist rail: top/bottom flanges, web, trolley wheels and hanging chain.
for z in [2.75,3.03]:B('Hoist_rail_flange',(32,-14,z),(.30,8.6,.045),yellow)
B('Hoist_rail_web',(32,-14,2.89),(.045,8.6,.24))
for x in [31.88,32.12]:
 for y in [-14.2,-13.8]:C('Hoist_trolley_wheel',(x,y,2.76),.10,.08,steel,'X')
B('Chain_hoist',(32,-14,2.45),(.26,.4,.38),yellow,.045)
P('Hoist_chain',[(32,-14,2.22),(32,-14,1.62)],.012,steel)
P('Hoist_hook',[(32,-14,1.62),(32,-14,1.48),(32.10,-14,1.40),(32.18,-14,1.47),(32.16,-14,1.56)],.025,zinc)
for x in [28.25,34.8]:
 for y in [-17,-12]:
  B('Ceiling_lamp_housing',(x,y,3.13),(.22,1.18,.12),steel)
  B('Ceiling_lamp_diffuser',(x,y,3.06),(.17,1.07,.018),lamp,.005)
for x in [30.42,33.58]:B('Service_aisle_line',(x,-13.6,-.994),(.055,5.85,.007),yellow,.001)
B('Emergency_stop_plate',(27.18,-14.0,.45),(.09,.26,.35),yellow)
C('Emergency_stop',(27.24,-14,.48),.065,.08,red,'X')
# Horizontal vessel, dished heads and two profiled saddle webs.
group=col('VF08_06_Diesel_Tank');tank=group
B('Bund_foundation',(32,-22.7,-1.24),(10,5.1,.48),concrete,.025)
for x in [27.12,36.88]:B('Bund_side',(x,-22.7,-.76),(.24,5.1,.48),concrete,.015)
for y in [-25.13,-20.27]:B('Bund_end',(32,y,-.76),(9.5,.24,.48),concrete,.015)
# Shell axis X, tangent curved end caps avoid overlapping flat cylinder end faces.
vs=[];faces=[];N=96
profile=[(-3.25,0),(-3.2,.3),(-3.07,.65),(-2.88,.92),(-2.7,1.1),(2.7,1.1),(2.88,.92),(3.07,.65),(3.2,.3),(3.25,0)]
for x,r in profile:
 for i in range(N):a=i*2*math.pi/N;vs.append((32+x,-22.7+r*math.cos(a),.55+r*math.sin(a)))
for j in range(len(profile)-1):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
o=mesh('VF08_Dished_horizontal_shell',vs,faces,blue)
for f in o.data.polygons:f.use_smooth=True
for x in [29.3,30.2,32,33.8,34.7]:ring('Tank_weld_band',(x,-22.7,.55),1.112,.045,zinc)
for x in [30.2,33.8]:
 B('Saddle_base',(x,-22.7,-.91),(.68,2.65,.12),steel)
 # Curved upper cut follows the tank underside, with a small bearing pad.
 ys=[-1.2+i*2.4/32 for i in range(33)];outline=[(y,.55-math.sqrt(max(0,1.115**2-y*y))-.015) for y in ys];outline=[(-1.2,-.85)]+outline+[(1.2,-.85)]
 vv=[(x+dx,-22.7+y,z) for dx in [-.16,.16] for y,z in outline];nn=len(outline)
 ff=[tuple(reversed(range(nn))),tuple(range(nn,nn*2))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
 mesh('VF08_Profiled_saddle',vv,ff,steel)
 for y in [-23.8,-21.6]:
  B('Saddle_gusset',(x,y,-.63),(.55,.06,.48),steel)
  bolt((x+.23,y,-.835),'Z');bolt((x-.23,y,-.835),'Z')
 C('Hold_down_stud',(x,-23.83,-.51),.018,.58,zinc)
# Manway, normal vent, emergency relief and mechanical level instrument.
C('Manway_neck',(33.1,-22.7,1.73),.34,.22,blue)
flange('Manway_bolted_cover',(33.1,-22.7,1.86),.39)
P('Normal_vent',[(34,-22.7,1.58),(34,-22.7,2.72),(34,-22.48,2.8)],.055,zinc)
C('Vent_weather_cap',(34,-22.48,2.83),.14,.05,steel)
C('Emergency_relief',(32,-22.7,1.83),.16,.34,zinc)
C('Relief_cap',(32,-22.7,2.02),.21,.055,steel)
B('Tank_identification_plate',(32,-23.812,.67),(1.45,.045,.47),cream,.012)
label('DIESEL  /  T-01',(32,-23.84,.72),.17,mat=steel)
label('STATION RESERVE',(32,-23.84,.53),.095,mat=steel)
# Ground-level filling is a deliberate gameplay station, outside the bund.
group=col('VF08_07_Fill_and_Fuel_Lines');fill=group
B('Fill_access_pad',(25.85,-22.4,-1.16),(2.25,5.7,.32),concrete,.012)
B('Fill_cabinet_pedestal',(26.8,-23.15,-.55),(.55,.65,.9),steel)
B('Fill_cabinet',(26.75,-23.15,.22),(.55,1.12,.92),green,.025)
B('Fill_cabinet_recess',(26.452,-23.15,.22),(.035,1.02,.8),steel,.01)
B('Spill_tray',(26.25,-23.15,-.22),(.46,1.16,.055),zinc)
for y in [-23.6,-22.7]:
 C('Capped_fill_coupling',(26.39,y,.14),.075,.15,zinc,'X')
 C('Coupling_dust_cap',(26.30,y,.14),.084,.035,steel,'X')
P('Bulk_fill_riser',[(26.85,-23.6,.1),(27.5,-23.6,.1),(28.7,-23.6,.1),(28.7,-22.7,1.95),(29.6,-22.7,1.95),(29.6,-22.7,1.58)],.047,zinc)
P('Emergency_pump_fill',[(26.85,-22.7,.1),(28,-22.7,.1),(28,-22.7,1.9),(30.1,-22.7,1.9),(30.1,-22.7,1.58)],.025,zinc)
C('Hand_pump_body',(26.15,-22.5,.38),.08,.35,steel)
P('Pump_handle',[(26.15,-22.5,.5),(26.05,-22.5,.72),(25.80,-22.5,.72)],.025,red)
P('Pump_suction',[(26.15,-22.5,.2),(26.15,-22.2,-.1),(25.7,-22.2,-.4),(25.55,-22.2,-.25)],.018,rubber)
P('Pump_outlet',[(26.15,-22.5,.3),(26.39,-22.7,.14)],.023,zinc)
label('FILL  /  HAND PUMP',(26.40,-23.15,.5),.08,(math.pi/2,0,-math.pi/2))
# Feed and return routed along bund edge, then through south wall to day tank.
for dx,m in [(0,zinc),(.12,blue)]:P('Fuel_feed_return',[(34.5+dx,-22.7,-.30),(35.4+dx,-22.7,-.3),(35.4+dx,-19.5,-.3),(35.4+dx,-19.5,.4),(35.4+dx,-18.55,.4)],.019,m)
B('Day_tank',(35.4,-18.45,-.12),(.85,.64,1.35),green,.045)
B('Day_tank_gauge',(34.956,-18.45,.1),(.025,.14,.8),cream)
P('Engine_fuel_feed',[(35.0,-18.4,-.5),(34,-18.4,-.65),(34,-13.5,-.65),(32.9,-13.5,-.2)],.018,zinc)
# Visible facade seams, fasteners and sheltered practical fittings.
group=shell
for x in [27.2,28,31.2,33.2,35.2,36.8]:
 B('Facade_cover_strip',(x,-19.145,1.2),(.055,.025,4.35),green,.002)
 for z in [-.75,.25,1.25,2.25,3.2]:bolt((x,-19.17,z),'Y')
for y in [-18.75,-16.3,-13.7,-11.3,-9.25]:
 B('West_cover_strip',(26.854,y,1.2),(.025,.055,4.35),green,.002)
 for z in [-.75,.25,1.25,2.25,3.2]:bolt((26.83,y,z),'X')
B('South_door_canopy',(29.5,-19.52,1.89),(2.05,1.05,.08),steel)
B('South_bulkhead',(30.65,-19.2,1.47),(.20,.15,.4),steel)
B('South_bulkhead_glass',(30.65,-19.29,1.47),(.145,.025,.32),lamp)
B('Station_power_sign',(28.05,-19.18,1.7),(1.35,.04,.38),cream)
label('POWER HOUSE',(28.05,-19.209,1.69),.12,mat=steel)
# Open door leaf parked clear of the 1.6 m south opening, with hinge barrels.
B('Open_service_door',(27.895,-19.24,.31),(1.47,.065,2.62),green,.02)
for z in [-.55,.3,1.17]:C('Door_hinge',(28.66,-19.18,z),.026,.15,zinc)
B('Door_push_bar',(27.9,-19.295,.2),(1.05,.035,.05),zinc)
# Open-ended radiator discharge plenum and flexible connection collar.
group=systems
mesh('VF08_Radiator_discharge_plenum',[(31,-11.02,-.55),(33,-11.02,-.55),(33,-11.02,1.45),(31,-11.02,1.45),(29.96,-9.15,-.32),(34.04,-9.15,-.32),(34.04,-9.15,2.25),(29.96,-9.15,2.25)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],zinc)
for x in [31.01,32.99]:B('Radiator_flexible_collar',(x,-10.96,.45),(.04,.15,1.98),rubber)
group=tank
C('Tank_level_gauge',(34.0,-23.82,.72),.16,.065,steel,'Y')
C('Level_gauge_face',(34.0,-23.86,.72),.139,.008,cream,'Y')
P('Level_gauge_needle',[(34,-23.869,.72),(34.07,-23.869,.79)],.009,red)
for i in range(9):
 a=i*math.pi/6-math.pi/6
 P('Gauge_tick',[(34+.11*math.cos(a),-23.87,.72+.11*math.sin(a)),(34+.125*math.cos(a),-23.87,.72+.125*math.sin(a))],.003,steel)
# Terrain footprint grows locally; keep remote routes and water terrace at existing anchors.
group=col('VF08_08_Site_Transitions');site=group
B('South_service_walk',(32,-19.65,-1.1),(10.1,1.25,.2),concrete,.01)
B('West_connection',(26.35,-16.95,-1.1),(1.3,5.3,.2),concrete,.01)
terrain=bpy.data.objects.get('R11_Current_Terrain');changed=0
if terrain:
 for v in terrain.data.vertices:
  p=terrain.matrix_world@v.co;dx=max(25.2-p.x,0,p.x-41.6);dy=max(-25.6-p.y,0,p.y+8.6);d=math.hypot(dx,dy)
  if d<2.2 and p.z>-1.42:
   p.z+=(min(p.z,-1.42)-p.z)*(1-d/2.2);v.co=terrain.matrix_world.inverted()@p;changed+=1
# Clip only the inherited route's surface under the new landing, preserving approach.
def clip(poly,axis,value,keep_less):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[axis]<=value) if keep_less else (a[axis]>=value);ib=(b[axis]<=value) if keep_less else (b[axis]>=value)
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((value-a[axis])/(b[axis]-a[axis])))
 return out
for o in list(bpy.data.collections['VF07_Continuous_Service_Routes'].objects):
 if o.type!='MESH':continue
 a,b=bounds(o)
 if b.x<25.7 or a.x>27 or b.y<-19.6 or a.y>-14.3:continue
 vv=[];ff=[]
 for f in o.data.polygons:
  poly=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
  # Keep each part outside the rectangular landing, splitting the remaining polygon.
  pending=poly;parts=[]
  for ax,val,less in [(0,25.7,True),(0,27,False),(1,-19.6,True),(1,-14.3,False)]:
   part=clip(pending,ax,val,less) if pending else []
   if len(part)>=3:parts.append(part)
   pending=clip(pending,ax,val,not less) if pending else []
  for part in parts:
   off=len(vv);vv.extend([o.matrix_world.inverted()@p for p in part]);ff.append(tuple(range(off,len(vv))))
 mats=list(o.data.materials);me=bpy.data.meshes.new(o.name+'_landing_cut');me.from_pydata(vv,[],ff);me.update()
 for m in mats:me.materials.append(m)
 o.data=me
# Footings terminate below the graded apron, avoiding levitating foundations.
for x in [27,32,37,41]:
 for y in [-19,-9] if x<40 else [-18,-12]:B('Building_pier',(x,y,-1.73),(.7,.7,.95),concrete,.016)
# Presentation keeps the full station editable but focuses cameras/lights on this area.
stage=col('VF08_90_Presentation');group=stage
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
area('VF08_Key',(19,-30,18),(32,-16,0),4500,12,(1,.86,.69))
area('VF08_Sky',(43,-10,14),(32,-16,0),3500,10,(.67,.8,1))
area('VF08_Interior',(32,-14,3.15),(32,-14,-1),650,7,(1,.83,.6))
area('VF08_Fill',(25,-15,2),(32,-14,0),450,5,(.75,.86,1))
for o in stage.objects:
 if o.type=='LIGHT':o['presentation_only']=True
cams=[]
for name,p,t,lens in [('01_Generator_and_Fuel',(17,-34,13),(32,-17,.6),45),('02_Generator_Interior',(28.5,-17.8,1.1),(32,-12.7,.4),21),('03_Fuel_Filling',(22.2,-29,3.4),(30.5,-22.6,.3),42),('04_Machine_Service',(34.7,-17.3,1.1),(31.8,-13,.45),25),('05_Plant_Cutaway',(43,-30,14),(32,-14,0),45)]:cams.append(camera(name,p,t,lens))
s.camera=cams[0];s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except:pass
s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.exposure=.3
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='MATERIAL'
bpy.context.view_layer.update()
report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'removed_objects':deleted,'hall_bounds':[27,37,-19,-9,-1,3.4],'workshop_bounds':[37,41,-18,-12,-1,2.4],'tank_diameter_m':2.2,'tank_length_m':6.5,'generator_skid_m':[2,5.15],'terrain_vertices_changed':changed,'preserved_bounds':{k:v for k,v in original.items() if k in ['Gondola_Floor','Drive_Floor','Control_Floor','Quarters_Floor','Hall_Floor']},'new_collections':[c.name for c in bpy.data.collections if c.name.startswith('VF08_')]}
(OUT/'build_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Generator_Fuel_Refinement.blend'))
print('VF08_SAVED',flush=True)
