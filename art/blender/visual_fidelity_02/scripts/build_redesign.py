"""Independent architecture study; does not overwrite a station level."""
import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
src=(OUT.parent/'visual_fidelity_01/scripts/build_sample.py').read_text()
# Reuse the reviewed construction helpers, not its building or presentation scene.
exec(compile(src.split('# Coordinates are')[0],__file__,'exec'))
tree=ast.parse(src)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['panel','grating','guard','label','area','camera']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),__file__,'exec'))
assets.name='01_Control_and_Quarters'
def cylinder(name,p,r,depth,mat,axis='Z',vertices=16):
 vs=[(r*math.cos(i*2*math.pi/vertices),r*math.sin(i*2*math.pi/vertices),z) for z in [-depth/2,depth/2] for i in range(vertices)]
 faces=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
 o=mesh(name,vs,faces,mat,.001);o.location=p
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 return o
roof_objects=[];wall_sets={};records=[]
fabric=material('VF_Bedding',(.26,.31,.28),0,.95)
wood=material('VF_Desk_Timber',(.22,.13,.065),0,.77)
paper=material('VF_Paper',(.68,.65,.5),0,.9)
lamp=material('VF_Warm_Diffuser',(.8,.7,.4),0,.5)
lp=lamp.node_tree.nodes.get('Principled BSDF');lp.inputs['Emission Color'].default_value=(1,.72,.4,1);lp.inputs['Emission Strength'].default_value=3

def col(name):
 global group
 group=bpy.data.collections.new(name);s.collection.children.link(group);return group
def wall(axis,fixed,lo,hi,z,h,openings,paint,outward=1):
 start=set(group.objects)
 cuts=sorted(set([lo,hi]+[q for a,b,c,d in openings for q in [a,b]]))
 for a,b in zip(cuts,cuts[1:]):
  opening=next((v for v in openings if v[0]<=(a+b)/2<=v[1]),None)
  ranges=[(0,h)] if opening is None else [(0,opening[2]),(opening[3],h)]
  for low,high in ranges:
   if high-low<.01:continue
   n=max(1,round((b-a)/1.05))
   for i in range(n):panel(axis,fixed,a+(b-a)*i/n,a+(b-a)*(i+1)/n,z+low,z+high,outward,paint)
 return set(group.objects)-start
def window(axis,fixed,a,b,z0,z1):
 def p(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 def d(u,v,z):return (u,v,z) if axis=='X' else (v,u,z)
 for u in [a-.035,b+.035]:box('Window_return',p(u,fixed,(z0+z1)/2),d(.07,.3,z1-z0+.14),zinc)
 for z in [z0-.035,z1+.035]:box('Window_head_sill',p((a+b)/2,fixed,z),d(b-a+.14,.34,.07),zinc)
 n=max(1,round((b-a)/1.1))
 for i in range(n):
  mid=a+(b-a)*(i+.5)/n;box('Clear_glazing',p(mid,fixed+.018,(z0+z1)/2),d((b-a)/n-.04,.012,z1-z0-.04),glass,.001)
 for i in range(1,n):box('Window_mullion',p(a+(b-a)*i/n,fixed+.035,(z0+z1)/2),d(.04,.06,z1-z0),steel)
def building(name,x,y,w,d,z,h,paint,front,back=(),left=(),right=()):
 start=set(group.objects)
 box(name+'_Floor',(x+w/2,y+d/2,z-.14),(w+.2,d+.2,.28),concrete,.015)
 if z==0:
  for xx in [x+.22,x+w/2,x+w-.22]:
   for yy in [y+.22,y+d-.22]:box('Concrete_foundation_pier',(xx,yy,-.65),(.46,.46,.78),concrete,.014)
 for xx in [x,x+w]:
  for yy in [y,y+d]:box('Structural_corner',(xx,yy,z+h/2),(.18,.18,h),steel,.01)
 for axis,fixed,lo,hi,ops in [('X',y,x,x+w,back),('X',y+d,x,x+w,front),('Y',x,y,y+d,left),('Y',x+w,y,y+d,right)]:
  for zz in [z+.1,z+h-.09]:
   cursor=lo;segments=[]
   if zz<z+.2:
    for a,b,c,e in sorted(ops):
     if c==0:segments.append((cursor,a-.04));cursor=b+.04
   segments.append((cursor,hi))
   for a,b in segments:
    if b<=a:continue
    box('Perimeter_beam',((a+b)/2,fixed,zz) if axis=='X' else (fixed,(a+b)/2,zz),(b-a,.18,.18) if axis=='X' else (.18,b-a,.18),steel)
 walls=[]
 for axis,fixed,lo,hi,ops,outward in [('X',y+d,x,x+w,front,1),('X',y,x,x+w,back,-1),('Y',x,y,y+d,left,-1),('Y',x+w,y,y+d,right,1)]:
  walls.extend(wall(axis,fixed,lo,hi,z,h,ops,paint,outward))
  for a,b,c,e in ops:
   if c>0:window(axis,fixed,a,b,z+c,z+e)
   else:
    def p(u,v,zz):return (u,v,zz) if axis=='X' else (v,u,zz)
    def ds(u,v,zz):return (u,v,zz) if axis=='X' else (v,u,zz)
    for u in [a-.035,b+.035]:box('Door_return',p(u,fixed,z+e/2),ds(.07,.28,e),steel)
    box('Door_lintel',p((a+b)/2,fixed,z+e+.035),ds(b-a+.14,.28,.07),steel)
    box('Flush_threshold',p((a+b)/2,fixed,z+.012),ds(b-a,.38,.024),zinc,.003)
 roofstart=set(group.objects)
 box(name+'_Roof',(x+w/2,y+d/2,z+h+.09),(w+.36,d+.36,.18),steel,.012)
 for yy in [y-.16,y+d+.16]:box('Roof_flashing',(x+w/2,yy,z+h+.05),(w+.36,.05,.28),zinc)
 for xx in [x-.16,x+w+.16]:box('Roof_flashing',(xx,y+d/2,z+h+.05),(.05,d+.36,.28),zinc)
 for i in range(round(w/.3)+1):box('Roof_seam',(x+i*.3,y+d/2,z+h+.19),(.025,d+.28,.03),paint,.003)
 roof_objects.extend(set(group.objects)-roofstart)
 wall_sets[name]=walls
 records.append({'building':name,'footprint_m':[w,d],'floor_z_m':z,'height_m':h,'front_openings':front,'back_openings':back})
 return set(group.objects)-start

building('Control',0,0,5.8,5.2,0,3.15,blue,[(.45,3.65,1,2.4),(4.05,5.35,0,2.4)],left=[(1.4,2.7,0,2.4)])
lower_roofs=list(roof_objects)
# Keep standing seams only on the exposed lower roof, not through the upstairs floor.
for o in list(lower_roofs):
 if o.name.startswith('Roof_seam') and o.location.x>=.29:
  xx=o.location.x;bpy.data.objects.remove(o,do_unlink=True);lower_roofs.remove(o);roof_objects.remove(o)
  for a,b in [(-.14,.59),(4.81,5.34)]:box('Exposed_lower_roof_seam',(xx,(a+b)/2,3.34),(.025,b-a,.03),blue,.003)
# Enlarged from 20 to 30.16 square metres; front operation and rear storage are separate.
for x in [.85,1.65,2.45]:
 box('Control_console',(x,4.65,.48),(.74,.64,.96),steel,.016)
 box('Instrument_face',(x,4.64,1.02),(.69,.53,.11),cream)
 for dx in [-.17,.17]:cylinder('Dial_bezel',(x+dx,4.66,1.086),.075,.018,zinc);cylinder('Dial_face',(x+dx,4.66,1.099),.063,.005,paper)
 for dx in [-.20,0,.20]:cylinder('Control_switch',(x+dx,4.47,1.09),.019,.04,rubber)
for x in [.65,1.4,2.15]:
 box('Rear_equipment_cabinet',(x,.32,1.0),(.68,.45,2),steel)
 box('Cabinet_door',(x,.558,1.0),(.60,.025,1.86),cream)
 box('Cabinet_handle',(x+.23,.6,1.05),(.022,.04,.22),zinc)
 for zz in [.25,1.77]:
  for xx in [x-.24,x+.24]:bolt((xx,.58,zz))
box('Maintenance_worktop',(4.1,.53,.79),(2.25,.8,.08),wood)
for x in [3.1,5.1]:box('Workbench_leg',(x,.53,.37),(.07,.65,.75),steel)
box('Wall_noticeboard',(4.0,.15,1.9),(1.6,.07,.8),wood)
for x in [3.5,4.0,4.5]:box('Maintenance_sheet',(x,.19,1.93),(.32,.008,.47),paper,.001)
for z in [2.65,2.75]:beam('Cable_tray',(0.25,.25,z),(5.55,.25,z),.055,zinc)
box('Control_seat',(3.3,3.5,.49),(.52,.5,.13),fabric)
box('Control_seat_back',(3.3,3.25,.92),(.5,.1,.72),fabric)
cylinder('Seat_pedestal',(3.3,3.5,.23),.045,.46,steel)

quarters=col('02_Upper_Living_Radio')
building('Quarters',.4,.7,6.1,4,3.35,2.65,green,[(1.0,2.5,1,2.15),(3.4,5.6,.85,2.15)],back=[(5.35,6.4,0,2.3)],right=[(2.0,3.3,1,2.15)])
upper_roofs=[o for o in roof_objects if o not in lower_roofs]
for y in [1.1,4.35]:
 box('Cantilever_transfer_beam',(3.3,y,3.23),(6.6,.16,.24),steel)
 beam('Overhang_knee_brace',(5.67,y,2.45),(6.42,y,3.25),.12)
 for x in [5.68,6.34]:
  box('Connection_plate',(x,y+.1,3.23),(.22,.035,.32),steel)
  for z in [3.13,3.31]:bolt((x,y+.125,z))
# Bed, bedside cabinet, closet, writing/radio desk and a modest service shelf.
box('Bed_frame',(1.32,2.25,3.65),(1.25,2.15,.34),steel,.025)
box('Mattress',(1.32,2.25,3.89),(1.19,2.05,.2),cream,.07)
box('Wool_blanket',(1.32,2.65,4.01),(1.21,1.23,.07),fabric,.035)
box('Pillow',(1.32,1.52,4.045),(.79,.43,.12),paper,.09)
box('Bedside_locker',(2.3,1.55,3.63),(.48,.48,.56),wood,.018)
box('Wardrobe',(3.35,1.1,4.31),(1.05,.6,1.92),cream)
for x in [3.29,3.41]:box('Wardrobe_handle',(x,1.425,4.32),(.015,.05,.18),steel)
box('Radio_desk',(4.58,4.13,4.11),(2.3,.75,.075),wood,.015)
for x in [3.55,5.6]:box('Desk_leg',(x,4.13,3.73),(.06,.62,.75),steel)
box('Radio_receiver',(4.6,4.21,4.33),(.72,.34,.32),steel,.012)
box('Frequency_display',(4.6,4.025,4.38),(.42,.015,.08),lamp,.002)
for x in [4.31,4.86]:cylinder('Radio_tuning_knob',(x,4.01,4.29),.032,.04,zinc,'Y')
beam('Microphone_stalk',(5.25,4,4.16),(5.25,4,4.47),.017,zinc)
box('Microphone',(5.25,4,4.50),(.065,.05,.11),steel,.015)
box('Logbook',(3.9,3.98,4.165),(.3,.22,.03),paper)
box('Writing_chair',(4.45,3.25,3.84),(.5,.5,.1),fabric)
box('Writing_chair_back',(4.45,3.02,4.18),(.5,.09,.62),fabric)
for x in [4.25,4.65]:
 for y in [3.08,3.43]:box('Chair_leg',(x,y,3.59),(.03,.03,.48),steel)
box('Small_wall_shelf',(5.75,1.45,4.8),(.7,.35,.045),wood)
bpy.data.objects['Small_wall_shelf'].location=(4.9,.98,4.8)
for i in range(5):box('Reference_manual',(4.67+i*.085,.98,4.96),(.065,.22,.28),cream)
box('Pinboard',(4.2,.83,4.98),(1,.06,.55),wood)
for x in [3.9,4.2,4.5]:box('Radio_schedule',(x,.865,5.01),(.22,.008,.34),paper,.001)

decks=col('03_Mixed_Deck_and_Rear_Stair')
def solid(x0,x1,y0,y1,z=0):
 box('Steel_deck_plate',((x0+x1)/2,(y0+y1)/2,z-.022),(x1-x0,y1-y0,.044),steel,.004)
 for x in [x0+.07,x1-.07]:
  for y in [y0+.07,y1-.07]:bolt((x,y,z+.003),'Z')
 # Fine welded ribs at transitions, leaving broad flat sheet surface.
 for x in [x0+.018,x1-.018]:box('Panel_edge_strip',(x,(y0+y1)/2,z+.002),(.025,y1-y0,.008),zinc,.002)
def deck(x0,x1,y0,y1,pattern=True):
 n=max(1,round(x1-x0))
 for i in range(n):
  a=x0+(x1-x0)*i/n+.012;b=x0+(x1-x0)*(i+1)/n-.012
  (solid if pattern and i%3==1 else grating)(a,b,y0,y1)
 for y in [y0,y1]:box('Deck_long_channel',((x0+x1)/2,y,-.14),(x1-x0,.10,.22),steel)
 for i in range(n+1):box('Deck_cross_joist',(x0+(x1-x0)*i/n,(y0+y1)/2,-.12),(.07,y1-y0,.18),steel)
deck(-.2,7,5.39,7.2)
deck(5.99,7,-1.9,5.38)
deck(-.2,5.98,-1.9,-.2)
deck(-.7,7,-3.35,-1.92)
solid(-.7,.05,-1.92,-.35)
guard((-.7,-3.35,0),(7,-3.35,0))
guard((-.2,7.2,0),(3.8,7.2,0));guard((5.5,7.2,0),(7,7.2,0));guard((7,-1.9,0),(7,7.2,0))
# Straight rear staircase: 20 risers; landing bridges to upper rear doorway.
rise=3.35/20;going=.28
for i in range(20):
 x=.05+i*going;z=(i+1)*rise
 solid(x,x+.28,-1.72,-.47,z)
 box('Stair_nosing',(x+.265,-1.095,z+.003),(.026,1.25,.014),yellow,.002)
for y in [-1.77,-.42]:
 beam('Stair_stringer',(.02,y,.025),(5.66,y,3.25),.16)
 beam('Sloping_handrail',(.02,y,1.12),(5.66,y,4.39),.044,zinc)
 for i in [0,4,8,12,16,19]:
  x=.05+i*going;z=(i+1)*rise;beam('Stair_guard_post',(x,y,z),(x,y,z+1.05),.044,zinc)
solid(5.65,6.65,-1.85,.7,3.35)
solid(5.25,5.65,-.35,.7,3.35)
guard((6.65,-1.85,3.35),(6.65,.7,3.35));guard((5.65,-1.85,3.35),(6.65,-1.85,3.35))
for x in [5.7,6.6]:
 for y in [-1.7,.45]:box('Landing_support',(x,y,1.54),(.14,.14,3.54),steel)
for x,y in [(-.1,7),(3.3,7),(6.9,7),(6.9,-1.8)]:box('Deck_pier',(x,y,-.6),(.45,.45,1),concrete)

# The rest of the room family shares the same framing, aperture and cladding logic.
hall=col('04_Waiting_Hall')
building('Waiting_Hall',-10.6,-2.6,9.8,7.8,0,3.15,blue,[(-10,-7.5,.85,2.4),(-6.9,-4.6,.85,2.4),(-3.8,-2.3,0,2.4)],right=[(1.4,2.7,0,2.4)],back=[(-6.7,-5.2,0,2.4)])
for y in [-.7,2.1]:
 for x in [-8.5,-5.4]:
  box('Passenger_bench',(x,y,.48),(2.25,.52,.09),wood)
  box('Bench_back',(x,y-.23,.81),(2.25,.07,.65),wood)
  for xx in [x-.8,x+.8]:box('Bench_support',(xx,y,.22),(.07,.44,.44),steel)
box('Ticket_counter',(-2.0,3.5,.55),(1.4,.75,1.1),steel)
box('Ticket_counter_top',(-2.0,3.5,1.13),(1.5,.83,.07),wood)
box('Timetable_board',(-5.7,-2.45,1.9),(2.4,.08,1.1),cream)
for x in [-6.4,-5.7,-5.0]:box('Printed_timetable',(x,-2.395,1.9),(.55,.012,.82),paper)
group=decks;deck(-10.8,-.21,5.39,7.2);solid(-.8,0,1.35,2.75)

service=col('05_Maintenance_Buildings_Study')
building('Generator',11,-9,6,8,0,3.4,green,[(12.9,14.5,0,2.5)],back=[(13.3,14.7,0,2.4)],right=[(-5.9,-4.5,0,2.4)])
building('Workshop',17,-7.5,3,5,0,3.4,blue,[(17.6,19.4,1,2.5)],left=[(-5.9,-4.5,0,2.4)])
for x in [12.6,15.2]:
 box('Generator_plinth',(x,-5,.15),(1.6,3,.3),concrete)
 box('Generator_housing',(x,-5,.9),(1.35,2.5,1.2),steel,.06)
 for i in range(9):box('Cooling_louvre',(x,-3.73,.56+i*.08),(1.05,.04,.035),zinc)
box('Workshop_workbench',(19.4,-5,.84),(.7,3.4,.1),wood)
for y in [-6.4,-4]:box('Workshop_cabinet',(19.4,y,.39),(.65,.75,.78),steel)
for z in [1.7,2.3]:box('Workshop_shelf',(19.55,-5,z),(.5,3.5,.045),zinc)

relay=col('06_Relay_Hut_Study')
building('Relay_Hut',11,4,4,4,0,2.8,green,[(12.45,13.55,0,2.3)],right=[(5.5,6.8,1,2.2)])
for x in [11.7,12.5]:box('Relay_equipment_rack',(x,4.4,1.1),(.6,.55,2.2),steel)
box('Relay_worktop',(14.35,6,.8),(.65,2.3,.06),wood)

# Rear cable entry, rooftop aerial and sensible bolted base plates.
group=quarters
box('Quarters_ceiling_fixture',(3.5,2.8,5.96),(1.1,.3,.08),cream)
box('Quarters_light_diffuser',(3.5,2.8,5.91),(1,.23,.015),lamp)
group=assets
box('Control_ceiling_fixture',(2.8,2.5,3.04),(1.1,.3,.08),cream)
box('Control_light_diffuser',(2.8,2.5,2.99),(1,.23,.015),lamp)
group=quarters
beam('Radio_aerial_mast',(6.15,1,5.95),(6.15,1,8.0),.045,zinc)
for z in [6.5,7.0,7.5]:beam('Aerial_cross_element',(5.8,1,z),(6.5,1,z),.018,zinc)
box('Aerial_mount',(6.15,1,6.08),(.3,.3,.05),steel)
for x in [6.05,6.25]:
 for y in [.9,1.1]:bolt((x,y,6.115),'Z')

group=stage
floor=material('Stage',(.17,.19,.19),0,.95);box('Ground',(2,1,-1.15),(200,200,.2),floor,0)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.66,.74,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
area('Key',(0,9,15),(2,2,2),3000,10,(1,.92,.8));area('Fill',(12,4,10),(2,2,2),2000,8,(.75,.87,1));area('Rim',(-7,-8,13),(2,2,2),2600,8,(1,.96,.87))
area('Upper_room_light',(3.5,2.8,5.9),(3.5,2.8,3.4),100,2,(1,.83,.61))
area('Control_light',(2.8,2.5,3.06),(2.8,2.5,0),90,2,(1,.83,.61))
hero=camera('01_Control_Quarters',(16,17,11),(2.5,2.3,2.7),48)
rear=camera('02_Rear_Stair',(13,-13,9),(3,-.1,2.4),48)
inside=camera('03_Upper_Interior',(6.1,2.5,5.1),(2.3,3.0,4.1),23)
family=camera('04_Building_Family',(34,38,29),(4,-1,1.6),40)
family.data.type='ORTHO';family.data.ortho_scale=39
cut=camera('05_Control_Interior',(5.4,1.2,1.9),(1.9,3.0,1.0),22)
s.camera=hero;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='OPTIX'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Architecture_Redesign.blend'))
for cam in [hero,rear,inside,family,cut]:
 s.camera=cam;s.render.filepath=str(OUT/'renders'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
(OUT/'design_manifest.json').write_text(json.dumps({'buildings':records,'control_area_m2':5.8*5.2,'previous_area_m2':20,'quarters_area_m2':6.1*4,'cantilever_m':.7,'stair_risers':20,'riser_m':rise,'going_m':going,'stair_width_m':1.25,'status':'Blender design studies; service and relay positions are presentation placements, not approved level coordinates.'},indent=2))
print('REDESIGN_COMPLETE',flush=True)
