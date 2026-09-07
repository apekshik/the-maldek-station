"""Preserve revision 03 layout; add service detail, tank and matching utility decks."""
from pathlib import Path
prev=Path(__file__).resolve().parents[2]/'visual_fidelity_03/scripts/build_revision.py'
setup=prev.read_text().rsplit("exec(compile(code,__file__,'exec'))",1)[0]
exec(compile(setup,__file__,'exec'))
addition=r'''
# Utility details use direct mesh construction and remain independently editable.
details=col('07_Exterior_Utility_Details')
red=material('VF_Service_Red',(.34,.055,.032),.2,.58)
def pipe(name,a,b,r=.025,mat=zinc):
 a,b=Vector(a),Vector(b);o=cylinder(name,(a+b)/2,r,(b-a).length,mat)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def loop(name,center,r,tube,axis='Z',mat=zinc):
 vs=[];fs=[];n=48;m=8
 for i in range(n):
  a=2*math.pi*i/n
  for j in range(m):
   b=2*math.pi*j/m;v=((r+tube*math.cos(b))*math.cos(a),(r+tube*math.cos(b))*math.sin(a),tube*math.sin(b))
   if axis=='Y':v=(v[0],v[2],v[1])
   if axis=='X':v=(v[2],v[0],v[1])
   vs.append(tuple(Vector(center)+Vector(v)))
 for i in range(n):
  for j in range(m):fs.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
 return mesh(name,vs,fs,mat)
def textsign(body,p,size=.12,mat=cream):
 cu=bpy.data.curves.new('Service_lettering','FONT');cu.body=body;cu.size=size;cu.extrude=.0006;cu.align_x='CENTER'
 o=bpy.data.objects.new('Service_lettering',cu);group.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,math.pi);cu.materials.append(mat);return o
def junction(x,y,z):
 box('Electrical_enclosure',(x,y,z),(.38,.19,.5),cream,.015)
 box('Gasketed_cover',(x,y+.106,z),(.33,.024,.44),steel,.007)
 for xx in [x-.13,x+.13]:
  for zz in [z-.17,z+.17]:bolt((xx,y+.125,zz))
 box('Warning_plate',(x,y+.126,z+.065),(.11,.008,.13),yellow,.001)
 pipe('Cable_drop',(x,y,z+.25),(x,y,2.85),.018)
 for zz in [z+.38,2.55]:box('Conduit_saddle',(x,y-.01,zz),(.085,.07,.022),steel)
def vent(x,y,z,w=.7):
 box('Vent_frame',(x,y,z),(w,.09,.5),steel)
 for i in range(7):box('Weather_louvre',(x,y+.06,z-.19+i*.061),(w-.08,.09,.028),zinc,.002).rotation_euler.x=.25
def lightfixture(x,y,z):
 box('Bulkhead_housing',(x,y,z),(.42,.22,.12),steel)
 box('Bulkhead_diffuser',(x,y+.045,z-.065),(.34,.15,.014),lamp,.003)
 for xx in [x-.15,x+.15]:pipe('Lamp_guard',(xx,y+.135,z-.09),(xx,y+.135,z+.035),.009,steel)
def downpipe(x,y,top):
 pipe('Rainwater_downpipe',(x,y,.23),(x,y,top),.045)
 pipe('Drain_shoe',(x,y,.23),(x,y+.17,.12),.045)
 for zz in [.5,1.7,top-.25]:box('Pipe_standoff',(x,y-.07,zz),(.15,.16,.025),steel)
def reel(x,y,z):
 cylinder('Hose_reel_hub',(x,y,z),.07,.3,steel,'Y')
 for yy in [y-.12,y+.12]:cylinder('Hose_reel_flange',(x,yy,z),.24,.018,red,'Y')
 for i in range(6):loop('Wound_hose',(x,y-.085+i*.034,z),.17,.016,'Y',rubber)
 pipe('Hose_tail',(x+.16,y,z),(x+.16,y,.25),.016,rubber)
def facade(x0,x1,y,h,sign):
 pipe('Facade_conduit_header',(x0+.18,y+.17,h-.34),(x1-.18,y+.17,h-.34),.018)
 for x in [x0+.25,x1-.25]:
  junction(x,y+.22,1.45);downpipe(x,y+.28,h)
 # Gutter trough and end caps express where rainwater goes.
 box('Gutter_bottom',((x0+x1)/2,y+.24,h-.06),(x1-x0,.2,.035),zinc)
 box('Gutter_outer_lip',((x0+x1)/2,y+.34,h),(x1-x0,.025,.15),zinc)
 for x in [x0,x1]:box('Gutter_end',(x,y+.24,h),(.03,.22,.15),zinc)
 box('Building_identifier',((x0+x1)/2,y+.17,h-.4),(min(2.4,x1-x0-.8),.035,.22),steel)
 textsign(sign,((x0+x1)/2,y+.193,h-.445),.12)
facade(0,5.8,5.2,3.08,'01 / CONTROL')
lightfixture(4.7,5.42,2.65)
facade(-10.6,-.8,5.2,3.12,'MALDEK / ARRIVALS')
lightfixture(-3.05,5.42,2.7);vent(-7.2,5.38,2.65,.5)
facade(11,17,-1,3.35,'03 / GENERATOR')
lightfixture(13.7,-.76,2.8);vent(15.8,-.79,1.7)
facade(17,20,-2.5,3.35,'04 / WORKSHOP')
facade(11,15,8,2.75,'05 / RELAY')
lightfixture(13,8.23,2.5);vent(11.8,8.22,1.7,.5)
# Side-wall utilities are shallow and stay within the inner service band.
side_start=set(group.objects)
junction(2,0,1.4);vent(3.8,0,2,.8);reel(.9,.06,1.05)
newside=set(group.objects)-side_start
from mathutils import Matrix
for o in newside:
 bpy.context.view_layer.update();o.matrix_world=Matrix.Translation((5.97,0,0))@Matrix(((0,1,0,0),(1,0,0,0),(0,0,1,0),(0,0,0,1)))@o.matrix_world
# Upper service entry, front rain collection, and deliberate fixing plates.
pipe('Upper_gutter',(.4,6.6,6.25),(6.5,6.6,6.25),.06)
pipe('Upper_downpipe',(6.65,6.6,3.2),(6.65,6.6,6.25),.035)
for z in [3.4,4.7,6.1]:box('Upper_pipe_bracket',(6.59,6.58,z),(.17,.10,.025),steel)

utilitydeck=col('08_Utility_Decks')
def apron(x0,x1,y):
 tiled(x0,x1,y,y+.6,'grating');tiled(x0,x1,y+.6,y+3,'solid');tiled(x0,x1,y+3,y+3.65,'grating')
 for yy in [y,y+.6,y+3,y+3.65]:box('Utility_deck_girder',((x0+x1)/2,yy,-.20),(x1-x0,.1,.34),steel)
 for xx in [x0+.2,(x0+x1)/2,x1-.2]:
  for yy in [y+.25,y+3.4]:box('Utility_deck_pier',(xx,yy,-.64),(.32,.32,.95),concrete)
apron(10.8,20.2,-.8)
apron(10.8,15.2,8.2)
tiled(9.65,10.8,.1,2.2,'solid')
tiled(9.65,10.8,6.1,10.7,'solid')
# Connect the workshop's recessed frontage to the generator apron.
tiled(17.1,20.2,-2.3,-.8,'solid')
guard((10.8,2.85,0),(20.2,2.85,0));guard((20.2,-2.3,0),(20.2,2.85,0))
guard((10.8,11.85,0),(15.2,11.85,0))

tankcol=col('09_Water_Tower')
tx,ty=18,13.3
# Four braced columns and an exposed service pipe, echoing the supplied reference.
for dx in [-1.25,1.25]:
 for dy in [-1.25,1.25]:
  box('Tank_concrete_footing',(tx+dx,ty+dy,-.38),(.6,.6,.76),concrete,.018)
  box('Tank_base_plate',(tx+dx,ty+dy,.03),(.37,.37,.06),steel)
  beam('Tank_column',(tx+dx,ty+dy,.06),(tx+dx,ty+dy,3.05),.14,steel)
  for ax in [-.13,.13]:
   for ay in [-.13,.13]:bolt((tx+dx+ax,ty+dy+ay,.069),'Z')
for axis in ['X','Y']:
 for side in [-1.25,1.25]:
  def pt(u,z):return (tx+u,ty+side,z) if axis=='X' else (tx+side,ty+u,z)
  for z0,z1 in [(.22,1.6),(1.6,2.94)]:
   beam('Tank_X_brace',pt(-1.25,z0),pt(1.25,z1),.055)
   beam('Tank_X_brace',pt(1.25,z0),pt(-1.25,z1),.055)
  beam('Tank_top_bearer',pt(-1.55,3.01),pt(1.55,3.01),.19)
  for u in [-1.25,1.25]:
   for z in [.22,1.6,2.94]:box('Brace_gusset',pt(u,z),(.19,.12,.25),rust)
cylinder('Tank_lower_blue_courses',(tx,ty,3.86),1.48,1.66,blue,vertices=96)
cylinder('Tank_upper_zinc_courses',(tx,ty,5.47),1.48,1.56,zinc,vertices=96)
for z in [3.05+i*.32 for i in range(11)]:loop('Tank_rolled_band',(tx,ty,z),1.486,.018)
cylinder('Tank_closed_roof',(tx,ty,6.275),1.49,.055,zinc,vertices=96)
cylinder('Tank_inspection_hatch',(tx+.4,ty,6.32),.31,.065,steel,vertices=48)
loop('Hatch_rim',(tx+.4,ty,6.36),.29,.014)
for z in [6.8,7.35]:
 for i in range(48):
  a=i*2*math.pi/48;b=(i+1)*2*math.pi/48
  if 5*math.pi/12<(a+b)/2<7*math.pi/12:continue
  pipe('Tank_top_guard',(tx+1.46*math.cos(a),ty+1.46*math.sin(a),z),(tx+1.46*math.cos(b),ty+1.46*math.sin(b),z),.023)
for i in range(12):
 if i==3:continue
 a=i*math.pi/6;pipe('Tank_guard_stanchion',(tx+1.46*math.cos(a),ty+1.46*math.sin(a),6.3),(tx+1.46*math.cos(a),ty+1.46*math.sin(a),7.35),.023)
# Ladder on the far side; cage begins above ground-level access.
ly=ty+1.72
for x in [tx-.25,tx+.25]:pipe('Ladder_stile',(x,ly,.2),(x,ly,7.32),.025)
for i in range(24):pipe('Ladder_rung',(tx-.25,ly,.3+i*.29),(tx+.25,ly,.3+i*.29),.018)
for z in [2.2,3.1,4,4.9,5.8,6.7]:
 # Cage hoops are open toward the vessel; curved mesh uses explicit arc segments.
 for i in range(24):
  a=math.pi*i/24;b=math.pi*(i+1)/24
  pipe('Ladder_cage_hoop',(tx+.45*math.cos(a),ly+.45*math.sin(a),z),(tx+.45*math.cos(b),ly+.45*math.sin(b),z),.015)
for a in [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi]:pipe('Ladder_cage_upright',(tx+.45*math.cos(a),ly+.45*math.sin(a),2.2),(tx+.45*math.cos(a),ly+.45*math.sin(a),6.7),.015)
pipe('Tank_outlet',(tx,ty,.6),(tx,ty,3.1),.105)
pipe('Water_supply_header',(tx,ty,.6),(tx,ty-1.7,.6),.07)
cylinder('Valve_body',(tx,ty-1.35,.6),.13,.23,steel,'Y')
loop('Red_valve_wheel',(tx,ty-1.36,.89),.16,.016,'Z',red)
for a in [0,math.pi/2]:pipe('Valve_spoke',(tx-.15*math.cos(a),ty-1.36-.15*math.sin(a),.89),(tx+.15*math.cos(a),ty-1.36+.15*math.sin(a),.89),.009,red)
box('Water_id_plate',(tx,ty+1.49,4.95),(1.45,.025,.42),steel)
textsign('STATION WATER',(tx,ty+1.508,4.98),.13)
textsign('WT-01  /  SERVICE',(tx,ty+1.508,4.81),.085)
pipe('Overflow_pipe',(tx+1.56,ty,2.5),(tx+1.56,ty,6.05),.045)
pipe('Overflow_neck',(tx+1.4,ty,6.05),(tx+1.56,ty,6.05),.045)
for o in tankcol.objects:
 if o.name.startswith(('Tank_lower','Tank_upper','Tank_rolled_band')):
  for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
area('Tank_daylight',(23,19,12),(18,13.3,4),1600,6,(1,.94,.83))
group=utilitydeck
tiled(15.2,21,10.1,16.3,'solid')
for yy in [10.1,16.3]:box('Tank_deck_girder',(18.1,yy,-.23),(5.8,.16,.4),steel)
for xx in [15.2,18.1,21]:box('Tank_deck_crossbeam',(xx,13.2,-.23),(.16,6.2,.4),steel)
for xx in [15.4,20.8]:
 for yy in [10.3,16.1]:box('Tank_deck_foundation',(xx,yy,-.68),(.48,.48,1),concrete)
guard((15.2,16.3,0),(21,16.3,0));guard((21,10.1,0),(21,16.3,0))

props=col('10_Working_Station_Props')
# Purposeful equipment against walls, outside the broad promenade centerline.
reel(14.5,8.43,1.15)
box('Maintenance_storage',(18.85,-1.8,.7),(1.5,.55,1.4),steel)
for x in [18.48,19.22]:
 box('Storage_door',(x,-1.505,.72),(.69,.025,1.27),cream)
 box('Storage_pull',(x-.23,-1.475,.76),(.02,.04,.18),zinc)
box('Fire_equipment_backplate',(11.48,-.76,1.08),(.32,.04,.7),steel)
cylinder('Fire_extinguisher',(11.48,-.62,1.05),.1,.44,red)
pipe('Extinguisher_handle',(11.4,-.62,1.32),(11.56,-.62,1.32),.012,steel)
for x in [-8.8,-8.1]:
 box('Lidded_waste_bin',(x,5.6,.42),(.5,.48,.84),steel,.025)
 box('Bin_lid',(x,5.6,.86),(.54,.52,.06),zinc,.015)
box('Boot_scraper_tray',(4.68,5.6,.016),(.7,.33,.032),steel)
for i in range(9):box('Scraper_blade',(4.4+i*.068,5.6,.04),(.01,.29,.04),zinc,.001)
box('Relay_battery_box',(14.48,8.4,.32),(.55,.5,.64),steel)
box('Spare_parts_crate',(19.35,-2.05,1.56),(.52,.38,.24),wood,.009)
# Public bench is tucked into the hall frontage, not into the walking band.
box('Exterior_bench',(-5.5,5.57,.48),(2,.4,.09),wood)
for x in [-6.2,-4.8]:box('Bench_bracket',(x,5.5,.25),(.06,.4,.46),steel)

'''
idx=code.rfind("group=stage\nfloor=material('Stage'")
assert idx!=-1
code=code[:idx]+addition+code[idx:]
code=code.replace("guard((9.65,-7.15,0),(9.65,9.05,0));guard", "guard((9.65,-7.15,0),(9.65,.1,0));guard((9.65,2.2,0),(9.65,6.1,0));guard((9.65,8,0),(9.65,9.05,0));guard")
code=code.replace("bpy.ops.wm.save_as_mainfile(filepath=str(OUT/", "tankcam=camera('06_Water_Tower',(28,25,12),(18,13.3,3.5),42)\nservicecam=camera('07_Service_Detail',(21,7,4),(15,-.1,1.4),40)\nbpy.ops.wm.save_as_mainfile(filepath=str(OUT/")
code=code.replace("for cam in [hero,rear,inside,family,cut]:", "for cam in [hero,rear,inside,family,cut,tankcam,servicecam]:")
code=code.replace("family.data.ortho_scale=46", "family.data.ortho_scale=52")
exec(compile(code,__file__,'exec'))
