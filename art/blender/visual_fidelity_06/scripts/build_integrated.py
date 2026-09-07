"""Independent VF06 design study. R11 circulation + reviewed VF05 architecture.
Run with Blender --background --factory-startup --python this_file.py.
Never writes Unreal assets or previous Blender files.
"""
import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('C:/Users/apek-anna/Developer/the-maldek-station')
OUT=ROOT/'art/blender/visual_fidelity_06';OUT.mkdir(exist_ok=True)
random.seed(41)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/unreal_handoff/revision11/station_layout.blend'))
s=bpy.context.scene
s.render.use_compositing=False;s.render.use_sequencer=False
# One full, editable view; prior source view layers are presentation cutaways.
for vl in list(s.view_layers)[1:]:s.view_layers.remove(vl)
s.view_layers[0].name='Integrated station'
s.view_layers[0].use=True
def enable(lc):
 lc.exclude=False;lc.hide_viewport=False
 for c in lc.children:enable(c)
enable(s.view_layers[0].layer_collection)
for o in bpy.data.objects:o.hide_set(False)
bpy.context.view_layer.update()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])]
def remove(o):bpy.data.objects.remove(o,do_unlink=True)
original={o.name:[list(p) for p in bounds(o)] for o in bpy.data.objects if o.type=='MESH'}
for c in list(bpy.data.collections):
 if c.name.startswith(('16_','17_','90_','91_','92_','93_','20_Rain')):
  for o in list(c.objects):remove(o)
  bpy.data.collections.remove(c)
# Old shells are replaced only here; machinery, paths, stairs and dock remain.
for cn in ['02_Control_Room','03_Waiting_Hall']:
 for o in list(bpy.data.collections[cn].objects):remove(o)
for o in list(bpy.data.collections['13_Roofs'].objects):
 if o.name.startswith(('Control_Roof','Hall_Roof','Relay_Roof')):remove(o)
for o in list(bpy.data.collections['21_Maintenance'].objects):
 if o.name.startswith(('Service_Wall','Workshop_Roof','Generator_Roof')):remove(o)
for o in list(bpy.data.collections['09_Relay_and_Paths'].objects):
 if o.name.startswith(('Relay_North','Relay_South','Relay_Side')):remove(o)
# Inherited hidden collision and superseded blockout objects stay hidden.
for o in bpy.data.objects:
 if o.hide_render:o.hide_set(True)
for c in bpy.data.collections:
 c.hide_render=False;c.hide_viewport=False
baseobjects=set(bpy.data.objects)
stage=bpy.data.collections.new('VF06_Presentation');s.collection.children.link(stage)
def col(name):
 global group
 group=bpy.data.collections.new(name);s.collection.children.link(group);return group
group=col('VF06_New_Construction');assets=group
steel=bpy.data.materials.get('R02_Chipped_Painted_Steel');blue=steel
# Reuse only helper definitions, with no previous scene generation or side effects.
for file,names in [('visual_fidelity_01/scripts/build_sample.py',['material','mesh','box','beam','bolt','panel','area','camera']),('visual_fidelity_02/scripts/build_redesign.py',['cylinder','wall','window','building'])]:
 for n in ast.parse((ROOT/'art/blender'/file).read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module(body=[n],type_ignores=[]),str(OUT),'exec'))
def mat(name,color,metal=0,rough=.6):return material('VF06_'+name,color,metal,rough)
blue=mat('Petrol_paint',(.07,.22,.25),.28,.55);green=mat('Service_green',(.12,.22,.16),.2,.62)
steel=mat('Structural_steel',(.045,.066,.072),.72,.43);zinc=mat('Galvanized',(.42,.46,.46),.85,.38)
concrete=mat('Concrete',(.34,.35,.32),0,.84);cream=mat('Warm_enamel',(.63,.59,.46),.1,.62)
yellow=mat('Safety_ochre',(.65,.37,.04),.25,.52);rust=mat('Fastener_oxidation',(.2,.065,.023),.05,.8)
rubber=mat('Rubber',(.012,.017,.018),0,.77);glass=mat('Glass',(.8,.9,.92),0,.05)
p=glass.node_tree.nodes.get('Principled BSDF')
for key in ['Base Color','Normal','Roughness']:
 for l in list(p.inputs[key].links):glass.node_tree.links.remove(l)
p.inputs['Base Color'].default_value=(.82,.9,.92,1);p.inputs['Roughness'].default_value=.04;p.inputs['Transmission Weight'].default_value=.94
lamp=mat('Lamp',(.95,.77,.42));p=lamp.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.72,.36,1);p.inputs['Emission Strength'].default_value=3
roof_objects=[];wall_sets={};records=[]
terrain_grid=json.loads((ROOT/'art/unreal_handoff/revision11/terrain_grid.json').read_text())
terrain_cut_count=0
for v in terrain_grid['vertices']:
 dx=max(17.2-v[0],0,v[0]-24.8);dy=max(-21.8-v[1],0,v[1]+14.5);dist=math.hypot(dx,dy)
 if dist<2 and v[2]>-1.4:
  t=max(0,1-dist/2);v[2]+=(min(v[2],-1.4)-v[2])*t;terrain_cut_count+=1
def ground(x,y):
 g=terrain_grid;i=math.floor(x-g['xmin']);j=math.floor(y-g['ymin']);u=x-g['xmin']-i;v=y-g['ymin']-j;n=g['nx'];a=g['vertices']
 return a[j*n+i][2]*(1-u)*(1-v)+a[j*n+i+1][2]*u*(1-v)+a[(j+1)*n+i][2]*(1-u)*v+a[(j+1)*n+i+1][2]*u*v
# R11's imported landscape is a separate mesh; the layout file retains old terrain.
oldterrain=bpy.data.objects.get('Terrain_Cliff_And_Relay_Spur')
if oldterrain:remove(oldterrain)
tg=terrain_grid;nx=tg['nx'];ny=len(tg['vertices'])//nx
terrainobj=mesh('R11_Current_Terrain',tg['vertices'],[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)],concrete)
for c in list(terrainobj.users_collection):c.objects.unlink(terrainobj)
bpy.data.collections['15_Terrain'].objects.link(terrainobj)
def sign(text,loc,size=.18,rotation=(math.pi/2,0,math.pi),material=cream):
 cu=bpy.data.curves.new(text,'FONT');cu.body=text;cu.align_x='CENTER';cu.size=size;cu.extrude=.001
 o=bpy.data.objects.new(text,cu);group.objects.link(o);o.location=loc;o.rotation_euler=rotation;cu.materials.append(material);return o
def pipe(name,a,b,r=.024,material=zinc):
 a,b=Vector(a),Vector(b);o=cylinder(name,(a+b)/2,r,(b-a).length,material);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def rail(a,b):
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/1.5))
 for i in range(n+1):
  p=a+(b-a)*i/n;pipe('Guard_post',p,p+Vector((0,0,1.1)),.025)
  box('Bolted_guard_base',p+Vector((0,0,.02)),(.17,.17,.04),steel)
  for dx in [-.055,.055]:bolt(p+Vector((dx,.05,.043)),'Z')
 for h in [.55,1.1]:pipe('Tubular_guard',a+Vector((0,0,h)),b+Vector((0,0,h)),.025)
 beam('Toe_kick',a+Vector((0,0,.08)),b+Vector((0,0,.08)),.08,steel)
def shift_collection(c,delta):
 bpy.context.view_layer.update();tr=Matrix.Translation(Vector(delta))
 for o in c.objects:
  if o.parent is None:o.matrix_world=tr@o.matrix_world
def append_collection(name,new,delta,predicate=None):
 rows=[r for r in json.loads((OUT/'v5_objects.json').read_text()) if name in r['collections']]
 if predicate:
  rows=[r for r in rows if r['bounds'][0][0]>-.35 and r['bounds'][1][0]<6.9 and r['bounds'][0][1]>-2.3 and r['bounds'][1][1]<.72 and r['bounds'][1][2]>.14]
 with bpy.data.libraries.load(str(ROOT/'art/blender/visual_fidelity_05/Maldek_Architecture_Redesign.blend'),link=False) as (a,b):b.objects=[r['name'] for r in rows]
 c=bpy.data.collections.new(new);s.collection.children.link(c)
 for o in b.objects:c.objects.link(o)
 shift_collection(c,delta);print('APPENDED',new,len(c.objects),flush=True);return c
control=append_collection('01_Control_and_Quarters','VF06_Control',(-8,-5.2,4))
quarters=append_collection('02_Upper_Living_Radio','VF06_Quarters',(-8,-5.2,4))
hall=append_collection('04_Waiting_Hall','VF06_Waiting_Hall',(-7.2,-5.2,4))
def stair_part(o):
 a,b=bounds(o)
 return a.x>-.35 and b.x<6.9 and a.y>-2.3 and b.y<.72 and b.z>.14
stairs=append_collection('03_Mixed_Deck_and_Rear_Stair','VF06_Quarters_Rear_Stair',(-8,-5.2,4),stair_part)
details=append_collection('07_Exterior_Utility_Details','VF06_Transferred_Details',(0,0,0))
bpy.context.view_layer.update()
for o in list(details.objects):
 a,b=bounds(o);c=(a+b)/2
 if c.x<-.3:o.location+=Vector((-7.2,-5.2,4))
 elif c.x<7:o.location+=Vector((-8,-5.2,4))
 else:remove(o)
tank=append_collection('09_Water_Tower','VF06_Water_Tower',(-5,-36.3,-1))
# Canopy meets the upper projection at a proper edge, not through its floor.
group=col('VF06_Canopy_Junction')
for o in list(bpy.data.collections['13_Roofs'].objects):
 if o.name in ['Platform_Canopy','Canopy_Front']:remove(o)
box('West_canopy_clear_of_quarters',(-5,4.29,7.51),(6,5.62,.18),steel)
box('Front_canopy_clear_of_quarters',(.375,2.4,7.51),(3.25,4.8,.18),steel)
box('Canopy_corner_return',(-1.625,3.14,7.51),(.75,3.32,.18),steel)
box('Canopy_head_flashing',(-5,1.47,7.6),(6,.075,.36),zinc)
box('Cantilever_drip_cover',(-4.6,1.35,7.59),(6.5,.24,.05),zinc)
# The overlapping original west front post now terminates under the transfer slab.
o=bpy.data.objects.get('Canopy_Post.002')
if o:o.scale.z*=3.15/3.5;o.location.z-=.175
for x in [-7.85,-6.5,-5,-3.5,-2.15]:
 box('Canopy_standing_seam',(x,4.3,7.624),(.024,5.6,.038),zinc)
for x in [-7.7,-2.3]:beam('Canopy_edge_beam',(x,1.5,7.34),(x,7.05,7.34),.16,steel)
# New service shells retain exact R11 dimensions and all real route doors.
group=col('VF06_Maintenance_Shells')
building('Generator',27,-19,6,8,-1,3.4,green,[(29.3,30.7,0,2.4)],back=[(29.3,30.7,0,2.4)],left=[(-15.8,-14.2,0,2.5)],right=[(-16.3,-14.7,0,2.4)])
building('Workshop',33,-18,3,5,-1,3.4,blue,[(33.6,35.4,1,2.5)],left=[(-16.3,-14.7,0,2.4)])
group=col('VF06_Relay_Shell')
building('Relay',46,11,4,4,3,2.8,green,[(47.4,48.6,0,2.3)],back=[(47.4,48.6,0,2.3)],right=[(12.2,13.8,1,2.2)])
# Retain measured original service slabs, avoiding coincident floor surfaces.
for cn in ['VF06_Maintenance_Shells','VF06_Relay_Shell']:
 for o in list(bpy.data.collections[cn].objects):
  if '_Floor' in o.name:remove(o)
# Each grating tile is one mesh of real open bars, avoiding thousands of objects.
deck_rects=[]
def deck_rect(x0,x1,y0,y1,z,kind,record=True):
 if x1-x0<.005 or y1-y0<.005:return
 if record:deck_rects.append([x0,x1,y0,y1,z,kind])
 nx=max(1,math.ceil((x1-x0)/1.5));ny=max(1,math.ceil((y1-y0)/1.5))
 for ix in range(nx):
  for iy in range(ny):
   a=x0+(x1-x0)*ix/nx+.005;b=x0+(x1-x0)*(ix+1)/nx-.005;c=y0+(y1-y0)*iy/ny+.005;d=y0+(y1-y0)*(iy+1)/ny-.005
   if kind=='plate':box('Flush_steel_plate',((a+b)/2,(c+d)/2,z-.03),(b-a,d-c,.06),blue,.003)
   else:
    verts=[];faces=[]
    def bar(cx,cy,w,h,depth):
     n=len(verts);verts.extend([(cx+sx*w/2,cy+sy*h/2,z+sz*depth) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)]])
     faces.extend([tuple(n+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
    for x in [a+.015,b-.015]:bar(x,(c+d)/2,.03,d-c,.06)
    for y in [c+.015,d-.015]:bar((a+b)/2,y,b-a,.03,.06)
    for i in range(1,int((b-a)/.045)):bar(a+i*.045,(c+d)/2,.006,d-c-.045,.048)
    for i in range(1,int((d-c)/.16)):bar((a+b)/2,c+i*.16,b-a-.045,.009,.025)
    mesh('Open_grating_tile',verts,faces,zinc,.001)
   for x in [a+.09,b-.09]:
    for y in [c+.09,d-.09]:bolt((x,y,z+.002),'Z')
 for y in [y0,y1]:box('Band_edge_channel',((x0+x1)/2,y,z-.17),(x1-x0,.1,.24),steel)
 for i in range(nx+1):box('Deck_joist',(x0+(x1-x0)*i/nx,(y0+y1)/2,z-.14),(.08,y1-y0,.2),steel)
group=col('VF06_Banded_Public_Deck')
# Bands measured outward: 1.8 m open / 3.6 m plate / 1.95 m open.
for a,b,k in [(0,1.8,'grate'),(1.8,5.4,'plate'),(5.4,7.35,'grate')]:
 deck_rect(-17.8,-8,a,b,4,k)
 deck_rect(-17.8-b,-17.8-a,-15.15,7.35,4,k)
 # Rear hall promenade has a permanent void for the existing arrival stair.
 for x0,x1 in [(-17.8,-14.2),(-11.6,-8)]:deck_rect(x0,x1,-7.8-b,-7.8-a,4,k)
 deck_rect(-8,-1.3,-5.2-b,-5.2-a,4,k)
# Original concrete dock panels receive metal finish; no apertures filled.
for o in bpy.data.collections['01_Upper_Platform'].objects:
 if o.name.startswith(('R04_Concrete_Finish','R04_Concrete_Slab')) and o.type=='MESH':o.data.materials.clear();o.data.materials.append(blue)
# West edge guard that formerly split hall and dock becomes an open connection.
for o in list(bpy.data.collections['01_Upper_Platform'].objects):
 a,b=bounds(o)
 if a.x<-7.85 and b.x<-7.8 and a.z>=4 and b.z<5.3 and not o.hide_render:remove(o)
for a,b in [((-25.15,-7.8,4),(-25.15,7.35,4)),((-25.15,7.35,4),(-8,7.35,4)),((-17.8,-15.15,4),(-14.2,-15.15,4)),((-11.6,-15.15,4),(-8,-15.15,4)),((-8,-12.55,4),(-1.3,-12.55,4)),((-14.2,-15.15,4),(-14.2,-9.3,4)),((-11.6,-15.15,4),(-11.6,-9.3,4)),((-1.3,-12.55,4),(-1.3,-5.2,4))]:rail(a,b)
# Outboard foundations leave the broad solid band clear of posts.
rail((-25.15,-15.15,4),(-25.15,-7.8,4));rail((-25.15,-15.15,4),(-17.8,-15.15,4))
for x,ys in [(-24.5,[-7,0,6.7]),(-18.4,[-7,0,6.7]),(-8.6,[6.7]),(-16.7,[-14.5]),(-10.7,[-14.5]),(-7.2,[-11.9]),(-1.9,[-11.9])]:
 for y in ys:
  gz=min(ground(x,y),3.0)
  box('Deck_foundation',(x,y,gz-.2),(.85,.85,.7),concrete,.02)
  box('Outer_structural_column',(x,y,(gz+.15+3.7)/2),(.24,.24,3.7-gz-.15),steel)
  beam('Deck_knee_brace',(x,y,2.7),(x+.65,y,3.77),.13,steel)
# Lower gallery remains at z=0, with storage in the former generator footprint.
group=col('VF06_Lower_Gallery_Details')
for x in [-.9,.1,1.1]:
 box('Service_locker',(x,-5.65,1),(.85,.5,2),steel)
 box('Locker_front',(x,-5.385,1),(.77,.03,1.9),cream)
 box('Locker_pull',(x+.27,-5.35,1),(.03,.06,.2),zinc)
 for i in range(5):box('Locker_louvre',(x,-5.36,1.6+i*.04),(.5,.018,.012),steel)
box('Repair_bench',(3.5,-5.4,.92),(2.7,.85,.08),cream)
for x in [2.3,4.7]:box('Bench_leg',(x,-5.4,.44),(.08,.7,.88),steel)
for x in [2.7,3.4,4.1]:box('Parts_bin',(x,-5.5,1.09),(.5,.36,.26),blue)
sign('SERVICE / STORES',(.1,-5.3,2.45),.19)
for x in [-1.72,5.7]:
 pipe('Overhead_pipe',(x,.2,3.25),(x,6.7,3.25),.045)
 for y in [.5,2.5,4.5,6.5]:box('Pipe_wall_bracket',(x,y,3.22),(.2,.04,.16),steel)
for y in [1,3,5]:
 box('Lower_task_light',(1.8,y,3.42),(1.2,.2,.11),steel)
 box('Task_light_lens',(1.8,y,3.36),(1.08,.16,.025),lamp)
 area('Gallery_light',(1.8,y,3.28),(1.8,y,0),95,1,(1,.8,.55))
for x in [-1.72,5.65]:
 for y in [.45,1.7,2.95,4.2]:deck_rect(x-.11,x+.11,y,y+1.15,.006,'grate')
# Flush inspection plates and machine service boundary.
for x in [.0,1.25,2.5,3.75]:
 for y in [1,2.3,3.6]:deck_rect(x,x+1.18,y,y+1.22,.008,'plate')
for x in [-1.4,3.45]:box('Machine_keep_clear_stripe',(x,6.2,.012),(.06,3.1,.018),yellow)
box('Machine_keep_clear_stripe',(1.03,4.67,.012),(4.9,.06,.018),yellow)
for y in [5.3,6.1,6.9]:
 box('Machine_inspection_plate',(4.3,y,.018),(1.35,.7,.035),blue)
sign('DRIVE 01 / KEEP CLEAR',(3.3,.13,2.75),.18)
# Gondola retains its exact R11 movement pivot, floor and boarding aperture.
group=col('VF06_Gondola_Details')
for o in bpy.data.collections['12_Gondola'].objects:
 if o.type!='MESH' or o.hide_render:continue
 if any(t in o.name for t in ['Skin','Panel','Header','Corner','Skirt']):o.data.materials.clear();o.data.materials.append(blue)
 if 'Glass' in o.name:o.data.materials.clear();o.data.materials.append(glass)
for x in [-1.64,1.64]:
 for y in [5.28,5.9,7.4,8.9,10.4,10.88]:
  for z in [4.17,4.77]:bolt((x,y,z),'X')
 pipe('Cabin_rub_strip',(x,5.2,4.42),(x,10.95,4.42),.025,rubber)
for x in [-1.25,1.25]:
 for y in [6.5,8,9.5]:box('Upholstered_bench_pad',(x,y,4.5),(.42,1.4,.08),rubber,.03)
 pipe('Interior_grab_rail',(x,5.5,5.95),(x,10.6,5.95),.025)
for y in [6.4,9.6]:box('Cabin_ceiling_light',(0,y,6.275),(.8,.18,.045),lamp)
box('Door_track',(0,4.89,6.18),(1.42,.09,.09),zinc)
sign('MALDEK  /  01',(0,11.17,4.42),.22)
sign('MIND THE GAP',(0,4.78,4.01),.12,(0,0,0),yellow)
parent=bpy.data.objects['Gondola_MOVE_THIS'];bpy.context.view_layer.update()
for o in group.objects:
 mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
# Utility yard: water is separate from the existing diesel containment.
group=col('VF06_Water_Service_Terrace')
deck_rect(17.8,24.2,-21.2,-15,-1,'plate')
linkstart=set(group.objects)
deck_rect(19.8,22.2,-15,-12,-1,'grate')
bpy.context.view_layer.update()
shear=Matrix(((1,1/3,0,5),(0,1,0,0),(0,.1,1,1.5),(0,0,0,1)))
for o in set(group.objects)-linkstart:o.matrix_world=shear@o.matrix_world
for a,b in [((17.8,-21.2,-1),(24.2,-21.2,-1)),((17.8,-21.2,-1),(17.8,-15,-1)),((24.2,-21.2,-1),(24.2,-15,-1))]:rail(a,b)
for x in [18.2,23.8]:
 for y in [-20.8,-15.4]:
  gz=min(ground(x,y),-1.5);box('Water_terrace_footing',(x,y,(gz-1)/2),(.75,.75,-1-gz),concrete)
pipe('Water_supply_main',(21,-18,-.45),(21,-12,-.45),.065,blue)
pipe('Water_supply_to_station',(21,-12,-.45),(11,-4,-.15),.065,blue)
pipe('Water_supply_riser',(11,-4,-.15),(11,-4,1),.065,blue)
box('Supply_valve_cabinet',(11,-4,1),(.55,.4,.55),cream)
sign('WATER / W-01',(21,-14.96,.5),.19)
# Practical exterior assemblies on the real service buildings.
group=col('VF06_Service_Hardware')
for x,y,z in [(28,-10.83,-1),(32,-10.83,-1),(49,15.17,3)]:
 box('Weatherproof_breaker',(x,y,z+1.3),(.5,.22,.65),cream)
 pipe('Electrical_conduit',(x,y,z+1.62),(x,y,z+2.85),.02)
 for h in [1.75,2.3,2.75]:box('Conduit_saddle',(x,y-.02,z+h),(.085,.08,.022),steel)
for x,y,z,w in [(30,-10.8,-1,2.4),(48,15.18,3,1.6)]:
 box('Entrance_light',(x,y,z+2.7),(.6,.25,.12),steel);box('Light_diffuser',(x,y+.02,z+2.635),(.5,.19,.018),lamp)
 box('Identification_plate',(x,y,z+3),(w,.06,.24),cream)
 sign('GENERATOR' if x==30 else 'RELAY',(x,y+.041,z+2.94),.16,material=steel)
# Recolor original roof and stair structures consistently, retaining their geometry.
for o in bpy.data.collections['21_Maintenance'].objects:
 if o.name.startswith('Service_Path'):o.location.z+=.012
for o in bpy.data.collections['VF06_Water_Service_Terrace'].objects:
 if o.name.startswith('Water_terrace_footing'):o.location.z-=.09
for o in bpy.data.objects:
 if o.type=='MESH' and o.name in ['Overlook','Lookout_Deck','Fuel_Yard','Generator_Yard_Link']:
  o.data.materials.clear();o.data.materials.append(blue)
for x in [2.2,3.6,5,6.4,7.8]:box('East_canopy_seam',(x,3.55,7.624),(.024,7.0,.038),zinc)
for cn in ['04_Lower_Drive','05_Generator_Room','07_Overlook','14_Site_Structure','21_Maintenance']:
 for o in bpy.data.collections[cn].objects:
  if o.type=='MESH' and not o.hide_render and any(t in o.name for t in ['Floor','Partition','Roof','Wall','Pad','Foot','Support']):
   o.data.materials.clear();o.data.materials.append(steel if 'Support' in o.name else concrete)
for o in baseobjects:
 try:name=o.name
 except ReferenceError:continue
 if name not in bpy.data.objects:continue
 if o.type=='MESH' and not o.hide_render and any(t in o.name for t in ['Canopy','Steel','Handrail','R04_Grating']):
  o.data.materials.clear();o.data.materials.append(steel if 'Canopy' in o.name else zinc)
# Remove obsolete entrance doors belonging to the replacement control shell.
for o in list(bpy.data.collections['11_Doors'].objects):remove(o)
# Review lighting / cameras; kept separate from game geometry.
group=stage
world=bpy.data.worlds.new('VF06_Daylight');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.4,.49,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.4;sun.angle=.15;o=bpy.data.objects.new('Sun',sun);stage.objects.link(o);o.rotation_euler=(.55,-.6,-.4)
area('Station_soft_fill',(-4,17,18),(-4,0,4),2200,12,(.8,.9,1))
area('Cabin_fill',(3,14,8),(0,8,5),450,4,(1,.89,.73))
area('Under_deck_fill',(8,13,5),(1,5,1),650,5,(.7,.83,1))
hero=camera('01_Integrated_Station',(-32,37,26),(-4,0,3),48);hero.data.type='ORTHO';hero.data.ortho_scale=48
site=camera('02_Whole_Site',(67,68,58),(13,0,2),45);site.data.type='ORTHO';site.data.ortho_scale=96
eye=camera('03_Dock_Approach',(-7,11,6),(-2,1,5.5),25)
lower=camera('04_Lower_Drive',(5.0,10.7,2),(1.5,3.5,1.4),23)
rear=camera('05_Rear_Arrival',(-23,-26,16),(-8,-5,5),45);rear.data.type='ORTHO';rear.data.ortho_scale=35
watercam=camera('06_Service_Yard',(42,-36,15),(26,-16,1),45);watercam.data.type='ORTHO';watercam.data.ortho_scale=31
plan=camera('07_Public_Plan',(-4,-1,55),(-4,-1,0),45);plan.data.type='ORTHO';plan.data.ortho_scale=48
lowplan=camera('08_Lower_Plan',(3,3,40),(3,3,0),45);lowplan.data.type='ORTHO';lowplan.data.ortho_scale=24
section=camera('09_Station_Section',(32,2,8),(-4,2,4.5),45);section.data.type='ORTHO';section.data.ortho_scale=32
quartercam=camera('10_Quarters',(-1.9,-3.9,9.15),(-5,-1.8,8.5),22)
s.camera=hero;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.exposure=.45
# Clear saved viewport hide state inherited from appending demonstration collections.
for c in [control,quarters,hall,stairs,details,tank]:
 for o in c.objects:o.hide_render=False;o.hide_set(False)
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='MATERIAL'
report={'source':'R11 station_layout.blend','live_world':json.loads((OUT/'live_unreal_audit.json').read_text())['world'],'bands_m':[1.8,3.6,1.95],'new_deck_rects':deck_rects,'unchanged_anchors':{},'design_changes':['Control 5.8 x 5.2 m at (-8,-5.2,4)','Quarters floor +7.65 m, projects 1.2 m north','West canopy starts at y=1.48 to clear cantilever','Water terrace centered near (21,-18,-1)','New deck bands stop at dock and arrival stair openings']}
for name in ['Gondola_Floor','Drive_Floor','Internal_Stair_Top_Steel','Internal_Lower_Landing_Steel','Exterior_Upper_Landing_Steel','Arrival_Upper_Landing','Generator_Floor.001','Workshop_Floor','Relay_Floor']:
 o=bpy.data.objects.get(name);b=[list(p) for p in bounds(o)];error=max(abs(b[i][j]-original[name][i][j]) for i in range(2) for j in range(3));report['unchanged_anchors'][name]={'bounds':b,'max_error_m':error};assert error<.0001,name
(OUT/'integration_report.json').write_text(json.dumps(report,indent=2))
report['proposed_water_terrace_terrain_cut_vertices']=terrain_cut_count
(OUT/'integration_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Integrated_Station.blend'))
print('VF06_BUILD_SAVED',flush=True)
