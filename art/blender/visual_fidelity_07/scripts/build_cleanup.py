"""VF07: connected walkable decks, relocated access stairs and graded service yard.
Loads VF06; writes only VF07. Blender 5.0 background script.
"""
import bpy,math,json,ast
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('C:/Users/apek-anna/Developer/the-maldek-station');OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'visual_fidelity_06/Maldek_Integrated_Station.blend'))
s=bpy.context.scene;bpy.context.view_layer.update()
steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized'];blue=bpy.data.materials['VF06_Petrol_paint'];concrete=bpy.data.materials['VF06_Concrete'];cream=bpy.data.materials['VF06_Warm_enamel'];yellow=bpy.data.materials['VF06_Safety_ochre'];rust=bpy.data.materials['VF06_Fastener_oxidation']
stage=bpy.data.collections['VF06_Presentation'];group=stage;assets=stage;deck_rects=[]
for rel,names in [('visual_fidelity_01/scripts/build_sample.py',['mesh','box','beam','bolt','material','camera','area']),('visual_fidelity_02/scripts/build_redesign.py',['cylinder']),('visual_fidelity_06/scripts/build_integrated.py',['bounds','col','pipe','rail','sign','deck_rect'])]:
 for n in ast.parse((OUT.parent/rel).read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module(body=[n],type_ignores=[]),rel,'exec'))
original={n:[list(v) for v in bounds(bpy.data.objects[n])] for n in ['Gondola_Floor','Drive_Floor','Control_Floor','Quarters_Floor','Hall_Floor'] if n in bpy.data.objects}
delete=set()
for cn in ['VF06_Banded_Public_Deck','VF06_Quarters_Rear_Stair','07_Overlook']:
 delete.update(bpy.data.collections[cn].objects)
for o in bpy.data.collections['01_Upper_Platform'].objects:
 a,b=bounds(o)
 if b.z>3.65 and not o.name.startswith(('Canopy_Post','Industrial_Lamp')):delete.add(o)
for o in bpy.data.collections['06_Stairs_and_Landings'].objects:
 if o.name.startswith('Exterior'):delete.add(o)
for o in bpy.data.collections['10_Parking_and_Arrival'].objects:
 if o.name.startswith(('Arrival','Parking_To_Stair')):delete.add(o)
for o in bpy.data.collections['21_Maintenance'].objects:
 if o.name.startswith('Service_Path'):delete.add(o)
delete.update(bpy.data.collections['08_Fuel_Yard'].objects)
for o in bpy.data.collections['VF06_Water_Service_Terrace'].objects:
 if o.name.startswith(('Water_supply','Supply_valve','WATER /')):delete.add(o)
for o in list(stage.objects):
 if o.type=='CAMERA':delete.add(o)
# The old overlook junction is now part of the larger east terrace.
for o in bpy.data.collections['20_Lookout_Bridge'].objects:
 a,b=bounds(o)
 if o.name=='Lookout_Junction_Extension' or (o.name.startswith(('Guard_','Bolted_Base')) and b.y<8.51 and a.y>6.3):delete.add(o)
bpy.data.batch_remove(ids=list(delete));bpy.context.view_layer.update()
o=bpy.data.objects.get('Timetable_board')
if o:o.location.x-=2.9
print('REMOVED_OBSOLETE',len(delete),flush=True)

# Platform has one material atlas and no retained opaque backing behind gratings.
group=col('VF07_Public_Deck');public=group
def deck(a,b,c,d,z,k):deck_rect(a,b,c,d,z,k)
for lo,hi,kind in [(0,1.8,'grate'),(1.8,5.4,'plate'),(5.4,7.35,'grate')]:
 deck(-17.8-hi,-17.8-lo,-15.15,7.35,4,kind)
 deck(-17.8,-8,lo,hi,4,kind)
 deck(-17.8,-8,-7.8-hi,-7.8-lo,4,kind)
# Complete the rear control platform; quarters stair occupies its outboard edge.
deck(-8,1.5,-7,-5.2,4,'grate');deck(-8,1.5,-10.6,-7,4,'plate');deck(-8,1.5,-13.2,-10.6,4,'grate')
# Full-width open strip against control facade, continuous with waiting-hall grating.
deck(-8,6,0,1.8,4,'grate')
deck(-8,-1.7,1.8,5.4,4,'plate');deck(-1.7,1.7,1.8,5.05,4,'plate');deck(1.7,6,1.8,5.4,4,'plate')
deck(-8,-4,5.4,7.35,4,'grate')
deck(-4,-1.7,5.4,11.5,4,'grate');deck(1.7,3.6,5.4,11.5,4,'grate');deck(3.6,6,5.4,8.4,4,'grate')
# East terrace: grating borders all exposed edges and joins both stair landings.
deck(8,15.35,2,3.95,4,'grate');deck(8,15.35,3.95,6.45,4,'plate');deck(8,15.35,6.45,8.4,4,'grate');deck(15.35,17.3,2,8.4,4,'grate')

# Outer guards are rebuilt from the finished footprint, never across a doorway.
group=col('VF07_Public_Guards')
segments=[((-25.15,-15.15),(-25.15,7.35)),((-25.15,7.35),(-4,7.35)),((-4,7.35),(-4,11.5)),((-4,11.5),(-1.7,11.5)),((1.7,11.5),(3.6,11.5)),((3.6,11.5),(3.6,8.4)),((3.6,8.4),(10.85,8.4)),((13.15,8.4),(17.3,8.4)),((17.3,8.4),(17.3,2)),((8,2),(15.3,2)),((8,2),(8,6.8)),((-2.05,0),(6,0)),((-25.15,-15.15),(-23,-15.15)),((-21,-15.15),(-8,-15.15)),((-8,-15.15),(-8,-13.2)),((-8,-13.2),(1.5,-13.2)),((1.5,-13.2),(1.5,-5.2)),((1.5,-5.2),(-2.1,-5.2))]
segments.remove(((17.3,8.4),(17.3,2)))
segments.extend([((17.3,8.4),(17.3,6.4)),((17.3,3.6),(17.3,2))])
for a,b in segments:rail((*a,4),(*b,4))
# The canopy support sits outside the continuous walking strip with a short head bracket.
o=bpy.data.objects.get('Canopy_Post')
if o:
 o.location.y+=.52
 box('Canopy_outboard_head',(-7.7,7.1,7.39),(.18,.5,.12),steel)

# Record walking centerlines and declared clear widths, used by independent checks.
routes=[]
def route(name,pts,width):routes.append(dict(name=name,points=[list(p) for p in pts],clear_width=width))
def simple_panel(x0,x1,y0,y1,z,name):
 before=set(group.objects);deck_rect(x0,x1,y0,y1,z,'grate',False)
 for o in set(group.objects)-before:
  if o.name.startswith(('Band_edge_channel','Deck_joist')):bpy.data.objects.remove(o,do_unlink=True)
  else:o['assembly']=name
def stair(name,start,direction,rise,n=24,width=1.8,going=.28):
 a=Vector(start);u=Vector((*direction,0)).normalized();v=Vector((-u.y,u.x,0));r=rise/n
 for i in range(n-1):
  c=a+u*((i+.5)*going)+Vector((0,0,(i+1)*r))
  if abs(u.x)>.5:simple_panel(c.x-going/2,c.x+going/2,c.y-width/2,c.y+width/2,c.z,name)
  else:simple_panel(c.x-width/2,c.x+width/2,c.y-going/2,c.y+going/2,c.z,name)
  beam(name+'_Nosing',c-u*(going/2-.018)-v*(width/2),c-u*(going/2-.018)+v*(width/2),.025,yellow)
 end=a+u*((n-1)*going)+Vector((0,0,rise))
 for side in [-1,1]:
  off=v*side*(width/2+.045)
  beam(name+'_Stringer',a+off+Vector((0,0,-.12)),end+off+Vector((0,0,-.16)),.16,steel)
  for i in range(0,n,3):
   p=a+u*(i*going)+off+Vector((0,0,min((i+1)*r,rise)))
   pipe(name+'_Post',p,p+Vector((0,0,1.05)),.025)
  for h in [.55,1.08]:pipe(name+'_Handrail',a+off+Vector((0,0,r+h)),end+off+Vector((0,0,h)),.025)
 points=[a-u*.55]+[a+u*((i+.5)*going)+Vector((0,0,(i+1)*r)) for i in range(n-1)]+[end+u*.45]
 route(name,points,width-.4);return end

group=col('VF07_Internal_Tread_Refresh')
for o in list(bpy.data.collections['06_Stairs_and_Landings'].objects):
 if o.name.startswith('Internal_Tread_') and o.name.endswith('_Open'):
  a,b=bounds(o);cy=(a.y+b.y)/2;z=b.z
  bpy.data.objects.remove(o,do_unlink=True)
  simple_panel(6.2,7.8,cy-.14,cy+.14,z,'Internal refreshed tread')

group=col('VF07_Sideways_Arrival')
# Climb west alongside the platform, turn north onto its edge, then walk to the hall.
end=stair('Arrival',(-14.56,-16.35,0),(-1,0),4,24,1.8)
deck(-14.56,-12.56,-17.8,-15.45,0,'grate');deck(-23,-21,-17.25,-15.15,4,'grate')
rail((-23,-17.25,4),(-21,-17.25,4));rail((-23,-17.25,4),(-23,-15.15,4))
rail((-12.56,-17.8,0),(-12.56,-15.45,0));rail((-12.56,-15.45,0),(-14.56,-15.45,0))
route('Arrival turn onto platform',[(-21.6,-16.35,4),(-22,-16.0,4),(-22,-14.3,4),(-18,-14.3,4)],1.2)
route('Completed rear hall approach',[(-13.15,-14.4,4),(-13.15,-8.1,4),(-13.15,-7.4,4)],1.1)

group=col('VF07_Quarters_Access')
# Outboard flight with a separate turning landing: no part starts at the hall wall.
stair('Quarters',(.4,-11.32,4),(0,1),3.65,20,1.6)
deck(-2.75,1.25,-6,-4.5,7.65,'grate')
rail((-2.75,-6,7.65),(-.4,-6,7.65));rail((1.25,-6,7.65),(1.25,-4.5,7.65));rail((1.25,-4.5,7.65),(-1.45,-4.5,7.65))
rail((-2.75,-6,7.65),(-2.75,-4.7,7.65))
route('Quarters landing and doorway',[(.4,-5.2,7.65),(-2.12,-5.2,7.65),(-2.12,-4.0,7.65)],.8)
route('Quarters lower approach',[(-1.5,-12.2,4),(.4,-12.2,4),(.4,-11.5,4)],1.1)
for x,y in [(1.25,-5.9),(1.25,-4.6),(-2.72,-5.9)]:box('Landing_column',(x,y,5.74),(.14,.14,3.75),steel)

group=col('VF07_Service_Descent')
stair('Exterior_service',(16.3,-4.44,0),(0,1),4,24,1.8)
deck(15.3,17.3,-6.3,-4.44,0,'grate')
route('Service descent lower exit',[(16.3,-5,0),(16.3,-6.7,0),(12,-6.7,0)],1.2)

# One lower apron replaces the former fuel slab + multiple road layers.
group=col('VF07_Service_Apron');apron=group
ax=[6,8.04,15.245,17.355,20];ay=[-9,-6.355,-4.385,-1.24,0]
av=[(x,y,0) for y in ay for x in ax];af=[]
for j in range(len(ay)-1):
 for i in range(len(ax)-1):
  x=(ax[i]+ax[i+1])/2;y=(ay[j]+ay[j+1])/2
  if (x<8.04 and y>-1.24) or (15.245<x<17.355 and -6.355<y<-4.385):continue
  k=j*len(ax)+i;af.append((k,k+1,k+1+len(ax),k+len(ax)))
o=mesh('Continuous_service_apron',av,af,concrete);m=o.modifiers.new('Slab with landing recesses','SOLIDIFY');m.thickness=.28;m.offset=-1
for x in [8,11,14,17]:box('Apron_expansion_joint',(x,-4.5,.003),(.018,8.94,.006),steel,.001)
for y in [-3,-6]:box('Apron_expansion_joint',(13,y,.003),(13.94,.018,.006),steel,.001)
# Small paved edge to join the preserved internal stair foot to the service floor.
# The original internal landing fills its own recess; no coincident infill slab.

roadmat=material('VF07_Compacted_Gravel',(.15,.16,.145),0,.92)
terrainmat=material('VF07_Terrain_Study',(.28,.29,.27),0,.95)
def spline(points,n=10):
 q=[Vector(points[0])]+[Vector(p) for p in points]+[Vector(points[-1])];out=[]
 for i in range(1,len(q)-2):
  a,b,c,d=q[i-1:i+3]
  for j in range(n):
   t=j/n;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 return out+[Vector(points[-1])]
def road(name,pts,width):
 vs=[];fs=[]
 for i,p in enumerate(pts):
  tan=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];side=Vector((-tan.y,tan.x,0)).normalized()
  vs.extend([tuple(p-side*width/2),tuple(p+side*width/2)])
 for i in range(len(pts)-1):k=2*i;fs.append((k,k+2,k+3,k+1))
 o=mesh(name,vs,fs,roadmat);mod=o.modifiers.new('Road base depth','SOLIDIFY');mod.thickness=.12;mod.offset=-1
 route(name,pts,1.0 if name.startswith('Relay') else 1.2);return o
group=col('VF07_Continuous_Service_Routes')
servicepath=spline([(18,-9,0),(18,-10,-.1),(22,-12,-.7),(27,-15,-1)])
relaypath=spline([(20,-3,0),(25,-3,.5),(30,-5,1.1),(40,2,2),(47.6,6.5,2.85),(48,8,3)])+[Vector((48,8+i*.25,3)) for i in range(1,13)]
returnpath=[Vector((48,15+i*.25,3)) for i in range(12)]+spline([(48,18,3),(47,22,3.5),(38,25,4.3),(29,21,4.5),(22,14,4.1),(19,8,4),(17.3,5,4)])
for o in list(bpy.data.collections['09_Relay_and_Paths'].objects):
 if o.name.startswith('Continuous_Relay_Path'):bpy.data.objects.remove(o,do_unlink=True)
road('Service_road',servicepath,2.4);road('Relay_outbound',relaypath,2.4);road('Relay_return',returnpath,2.4)
# Arrival still meets the existing forest approach at its former bottom-landing area.
arrivalpath=[Vector((-13.5,-19.5,0)),Vector((-13.5,-17.8,0))];road('Arrival_ground_approach',arrivalpath,1.8)

# Water main follows the service edge, below the apron instead of crossing its surface.
group=col('VF07_Water_Pipework')
waterpoints=[(21,-18,-.45),(17.2,-18,-.45),(17.2,-12,-.45),(15,-10,-.45),(8,-10,-.45),(6.2,-8,-.45),(6.2,-5,-.45),(6.2,-5,1.3)]
for a,b in zip(waterpoints,waterpoints[1:]):pipe('Water_main',a,b,.065,blue)
for y in [-5.2,-4.8]:box('Wall_pipe_bracket',(6.15,y,.9),(.22,.09,.12),steel)
box('Wall_water_valve',(6.19,-5,1.3),(.25,.42,.4),cream)
cylinder('Valve_wheel',(6.36,-5,1.3),.15,.035,yellow,'X')
sign('WATER',(6.33,-5,1.68),.1,(math.pi/2,0,math.pi/2))

# Resample local ground at 0.5 m; cut a graded service bench and blend road verges.
# Buildings, gondola and floor heights remain anchored; only the troublesome ground changes.
print('GRADING_TERRAIN',flush=True)
terrain=bpy.data.objects['R11_Current_Terrain'];old=terrain.data
grid={(round(v.co.x,3),round(v.co.y,3)):v.co.z for v in old.vertices}
def oldground(x,y):
 x0=math.floor(x);y0=math.floor(y);u=x-x0;v=y-y0
 return sum(grid.get((xx,yy),grid.get((x0,y0),-10))*w for xx,yy,w in [(x0,y0,(1-u)*(1-v)),(x0+1,y0,u*(1-v)),(x0,y0+1,(1-u)*v),(x0+1,y0+1,u*v)])
def near(x,y,points):
 best=1e9;z=0
 for a,b in zip(points,points[1:]):
  dx=b.x-a.x;dy=b.y-a.y;l=dx*dx+dy*dy
  if l<1e-8:continue
  t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/l));dist=(x-a.x-t*dx)**2+(y-a.y-t*dy)**2
  if dist<best:best=dist;z=a.z+t*(b.z-a.z)
 return math.sqrt(best),z
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def grade(x,y):
 h=oldground(x,y)
 dist=math.hypot(max(5.7-x,0,x-31.5),max(-20-y,0,y-8.7));w=1-smooth(dist/3)
 target=-.22-.045*max(0,x-14)-.025*max(0,-y-6)
 if w:h=h*(1-w)+min(h,target)*w
 for a,b,c,d,z in [(5.7,20.1,-9,8.7,-.22),(-15,-12,-18,-15.3,-.22),(-23.2,-14.4,-17.6,-15.3,-.22)]:
  dist=math.hypot(max(a-x,0,x-b),max(c-y,0,y-d));w=1-smooth(dist/3)
  if w:h=h*(1-w)+min(h,z)*w
 if 3<x<54 and -24<y<29:
  for pts in [servicepath,relaypath,returnpath]:
   dist,z=near(x,y,pts)
   if dist<3.3:
    w=1-smooth((dist-1.45)/1.85);h=h*(1-w)+(z-.17)*w
 if -16<x<-11 and -21<y<-15:
  dist,z=near(x,y,arrivalpath);w=1-smooth((dist-1)/1.5);h=h*(1-w)+(z-.17)*w
 return h
xs=list(range(-96,-30))+[-30+i*.5 for i in range(133)]+list(range(37,113))
ys=list(range(-80,-26))+[-26+i*.5 for i in range(113)]+list(range(31,97))
verts=[(x,y,grade(x,y)) for y in ys for x in xs];nx=len(xs)
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)]
me=bpy.data.meshes.new('Graded_terrain');me.from_pydata(verts,[],faces);me.update();terrain.data=me;me.materials.append(terrainmat)
for p in me.polygons:p.use_smooth=True

# Carry the new decks with supports outside walking space; ground every new footing.
group=col('VF07_Deck_Structure')
supports=[(-24.5,y) for y in [-14.5,-7,0,6.7]]+[(-18.4,y) for y in [-14.5,-7,0,6.7]]+[(-8.6,6.7),(-8.6,-14.5),(1.35,-12.7),(1.35,-5.6),(-7.2,-12.7),(-4,10.9),(3.55,10.9),(5.65,7.8),(16.9,7.9),(16.9,2.3),(8.7,7.9),(9,2.3),(-22.8,-16.9)]
for x,y in supports:
 gz=grade(x,y);top=3.72
 low=min(grade(x+dx,y+dy) for dx in [-.4,0,.4] for dy in [-.4,0,.4])-.2
 box('Grounded_footing',(x,y,(low+gz+.12)/2),(.8,.8,gz+.12-low),concrete)
 box('Deck_column',(x,y,(gz+.12+top)/2),(.2,.2,top-gz-.12),steel)
 beam('Deck_brace',(x,y,top-1),(x+.6,y,top),.12,steel)
 # The post terminates below the walking surface; upper guards have separate bases.
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.hide_render or 'VF07_' in ','.join(c.name for c in o.users_collection):continue
 a,b=bounds(o);c=(a+b)/2;size=b-a
 if 6<c.x<21 and -10<c.y<10:
  gz=grade(c.x,c.y)
  if any(n in o.name.lower() for n in ['footing','foundation','bedrock','concrete_foot']) and max(size.x,size.y)<2 and size.z<1.2:o.location.z+=gz+.08-c.z
  elif any(n in o.name.lower() for n in ['support','column','leg']) and size.z>2 and max(size.x,size.y)<.4 and a.z<3:
   factor=(b.z-gz-.15)/size.z;o.matrix_world=Matrix.Translation((0,0,b.z))@Matrix.Diagonal((1,1,factor,1))@Matrix.Translation((0,0,-b.z))@o.matrix_world

# Re-anchor bridge backstays after cutting away the obsolete terrain mound.
for o in list(bpy.data.collections['20_Lookout_Bridge'].objects):
 if o.name.startswith(('Tower_Backstay','Backstay_Anchor')):bpy.data.objects.remove(o,do_unlink=True)
for x in [11,13]:
 z=grade(x,1)
 box('Backstay_ground_anchor',(x,1,z+.05),(.75,.75,.6),concrete)
 pipe('Reanchored_backstay',(x,1,z+.35),(x,7.5,14),.03,steel)

route('Control front approach',[(-3.3,2.7,4),(-3.3,.5,4),(-3.3,-.8,4)],1.0)
route('Front grating across facade',[(-7.2,.95,4),(-2.7,.95,4)],1.2)
route('West continuous border',[(-8.5,6.5,4),(-4.6,6.5,4),(-2.85,6.5,4),(-2.85,10.6,4)],1.2)
route('East terrace grating',[(8.5,6.7,4),(16.25,6.7,4),(16.25,3.0,4)],1.2)
route('Boarding threshold',[(0,4.5,4),(0,5.4,4)],1.0)
route('Internal descending stair',[(7,.5+i*.28,(i+1)/6) for i in range(23)],1.2)

# Presentation cameras target each reported defect, plus the whole assembly.
group=stage
def cam(n,p,t,scale=None,lens=43):
 o=camera(n,p,t,lens)
 if scale:o.data.type='ORTHO';o.data.ortho_scale=scale
 return o
hero=cam('01_Connected_Station',(-33,34,26),(-4,-2,3),52)
cam('02_Sideways_Arrival',(-30,-31,19),(-13,-9,4),36)
cam('03_Clear_Control_Entry',(-1.9,3.8,6.3),(-4.5,.1,4.85),None,28)
cam('04_Quarters_Stair',(11,-20,16),(-2,-6.5,6),23)
cam('05_Clean_Service_Descent',(28,-23,17),(13,-3,2),34)
cam('06_Continuous_Dock_Border',(-15,16,17),(-2,3,4),29)
cam('07_Water_And_Routes',(39,-34,17),(20,-11,0),37)
cam('08_Platform_Plan',(-4,-3,65),(-4,-3,0),53)
cam('09_Whole_Site',(70,66,63),(12,0,2),102)
cam('10_Stair_Walking_View',(.4,-12.5,5.6),(.4,-5.5,8.2),None,24)
s.camera=hero;s.view_layers[0].name='VF07 Full station';s.render.use_compositing=False;s.render.use_sequencer=False
s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=32
bpy.context.view_layer.update()
for ar in bpy.context.screen.areas:
 if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.overlay.show_overlays=False
report={'source':'VF06','changes':['Control doorway old railing removed','All public deck surfaces rebuilt with open grating borders','Arrival slot filled, arrival flight runs sideways','Quarters stair moved outboard with turning landing','Service apron replaces overlapping roads/slabs','Service stairs and routes receive graded terrain clearance','Water main rerouted below apron and along service edge'],'routes':routes,'deck_rects':deck_rects,'anchors':original,'water_pipe_centerline':waterpoints,'terrain_vertices':len(verts)}
(OUT/'layout.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Station_Cleanup.blend'));print('VF07_SAVED',flush=True)
