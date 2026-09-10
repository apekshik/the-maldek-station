"""Editable layout blockout, metre units. No Unreal import or station overwrite."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]; REPO=OUT.parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='01_Lodge_Layout';s.unit_settings.system='METRIC'
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
shell=collection('PL01_Shell');furn=collection('PL01_Furniture_Footprints');wet=collection('PL01_Restroom_Fixtures');markers=collection('PL01_Labels_and_Clearances');roof=collection('PL01_Roof_Envelope');stage=collection('PL01_Review')
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72;return m
pine=mat('Layout_Warm_Pine',(.32,.19,.085));cream=mat('Layout_Cream_Plaster',(.57,.52,.40));petrol=mat('Layout_Petrol_Enamel',(.055,.15,.13));tile=mat('Layout_Wet_Tile',(.22,.27,.24));floor=mat('Layout_Floor',(.24,.20,.145));gold=mat('Layout_Brass_Markers',(.8,.56,.19));dark=mat('Layout_Worktops',(.075,.095,.085));white=mat('Layout_Porcelain',(.7,.72,.63));route=mat('Layout_Protected_Route',(.16,.5,.35));gray=mat('Layout_Context',(.17,.21,.24))
blockers=[]
def box(n,x,d,z,w,l,h,m,c=furn,block=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x+w/2,-d-l/2,z+h/2));o=bpy.context.object;o.name=n;o.dimensions=(w,l,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m)
 if block and z+h>.15 and z<2.1: blockers.append((n,x,d,x+w,d+l,z,z+h))
 return o
def text(n,body,x,d,z,size=.19,flat=True,c=markers):
 curve=bpy.data.curves.new(n,'FONT');curve.body=body;curve.size=size;curve.extrude=.001
 o=bpy.data.objects.new(n,curve);c.objects.link(o);o.location=(x,-d,z);o.data.materials.append(gold)
 if not flat:o.rotation_euler=(math.pi/2,0,0)
 return o
def wall(n,axis,k,a,b,holes=()):
 cuts=sorted(set([a,b]+[v for q in holes for v in q[:2]]))
 for i,(u,v) in enumerate(zip(cuts,cuts[1:])):
  if u<a or v>b:continue
  q=next((q for q in holes if q[0]<=u and q[1]>=v),None)
  spans=[(0,3.2)] if q is None else [(0,q[2]),(q[3],3.2)]
  for z0,z1 in spans:
   if z1-z0<.001:continue
   x,d,w,l=(u,k,v-u,.18) if axis=='X' else (k,u,.18,v-u)
   box(f'{n}_{i}_{z0}',x,d,z0,w,l,z1-z0,cream,shell)
def path(n,pts,m=route,r=.025,c=markers):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(n,cu);c.objects.link(o);cu.materials.append(m);return o
def swing(n,x,d,width,ang0=0):
 pts=[(x+width*math.cos(ang0+t*math.pi/2/24),-d-width*math.sin(ang0+t*math.pi/2/24),.025) for t in range(25)]
 path(n,pts,gold,.015)
for n,x,d,w,l in [('Hall',0,0,14,11.2),('Coffee',0,11.2,5,5),('Restrooms',8,11.2,6,6)]:
 box(n+'_Floor',x,d,-.2,w,l,.2,floor if n=='Hall' else tile,shell,False)
 box(n+'_Roof_envelope',x,d,3.3,w,l,.16,petrol,roof,False)
box('Arrival_court_floor',5,11.2,-.2,3,6,.2,tile,shell,False)
wall('North','X',0,.18,13.82,[(1.4,5.2,.9,2.6),(6.4,7.6,0,2.3),(8.6,12.4,.9,2.6)])
wall('West','D',0,0,16.2);wall('East','D',13.82,0,17.2)
wall('Hall_south_coffee','X',11.02,.18,5,[(1,4,0,2.2)])
wall('Hall_south_entry','X',11.02,5,8,[(6.4,7.6,0,2.3)])
wall('Hall_south_WC','X',11.02,8,13.82,[(8.4,9.6,0,2.3)])
wall('Coffee_east','D',4.82,11.2,16.2,[(14,15,0,2.2)])
wall('Coffee_rear','X',16.02,.18,4.82)
wall('WC_west','D',8,11.2,17.2);wall('WC_rear','X',17.02,8.18,13.82)
wall('WC_hall_partition','X',13.02,8.18,13.82,[(10,10.9,0,2.2),(12,12.9,0,2.2)])
wall('WC_shared','D',10.91,13.2,17.02)
box('Full_height_privacy_screen',9.8,11.2,0,.18,.52,3.2,cream,shell)
for x in [1.4,8.6]:box('Frosted_window_placeholder',x,.065,.9,3.8,.05,1.7,white,shell,False)
for x in [6.4]:swing('North_door_sweep',x,0,1.2);swing('Court_door_sweep',x,11.02,1.2,-math.pi/2)
swing('Staff_door_sweep',4.82,14,1,-math.pi)
for x in [10,12]:swing('Restroom_door_sweep',x,13.02,.9)
for row,d in enumerate([1.1,4.3,7.5]):
 for col,x in enumerate([4,10]):
  k=row*2+col+1
  box(f'Table_{k:02}_Top',x,d,.74,1.8,.8,.07,pine)
  for legx in [x+.12,x+1.5]:box(f'Table_{k:02}_Leg',legx,d+.08,0,.16,.64,.74,petrol)
  for bd in [d-.55,d+1]:
   box(f'Bench_{k:02}_{bd}_Seat',x,bd,.44,1.8,.35,.07,pine)
   for lx in [x+.12,x+1.5]:box(f'Bench_{k:02}_Support',lx,bd,0,.16,.35,.44,petrol)
  text(f'Table_{k}_label',f'T{k:02}',x+.5,d+.5,.825,.22)
for i in range(12):
 x=10+i*.32;box(f'Locker_{i+1:02}',x,10.5,0,.30,.5,1.85,petrol)
 # Identifiable locker fronts and individually editable door proxies.
 box(f'Locker_{i+1:02}_Door',x+.01,10.475,.08,.28,.02,1.7,dark,block=False)
 text(f'Locker_{i+1:02}_Number',f'{i+1:02}',x+.05,10.465,1.5,.11,False)
box('Serving_counter',1,10.85,0,3,.65,1,pine)
box('Coffee_equipment_run',.25,12,0,.7,3.5,.9,dark)
box('Rear_prep_run',1.05,15.3,0,3.5,.65,.9,dark)
box('Dry_store',3.45,11.6,0,1.05,.55,2.1,petrol)
for n,x,d,w,l,h in [('Urn',.32,12.1,.48,.5,.6),('Kettle',.32,12.8,.42,.4,.35),('Wash_sink',.29,14.3,.6,.65,.08),('Hand_basin',.3,15.05,.45,.35,.08),('Microwave',1.3,15.35,.65,.5,.4)]:box(n+'_Proxy',x,d,.91,w,l,h,white)
box('Fridge_proxy',2.25,15.34,.05,.65,.58,.8,petrol)
box('Public_lost_property_cubby',4.22,10.6,.65,.5,.4,.55,pine)
text('Menu_placeholder','COFFEE / TEA / SNACKS',1,10.98,2.35,.17,False)
for i,d in enumerate([2.2,4.2,6.2]):box(f'Poster_frame_{i+1}',.19,d,1.15,.04,.75,1.05,pine,block=False)
for n,x,d,w,l in [('Women_A',8.25,15.3,1.2,1.6),('Women_B',9.6,15.3,1.2,1.6),('Men_A',11.2,15.3,1.25,1.6)]:
 box(n+'_WC',x+.35,d+.55,0,.5,.7,.45,white,wet)
 box(n+'_Left_partition',x,d,0,.06,l,2,petrol,wet)
 box(n+'_Right_partition',x+w-.06,d,0,.06,l,2,petrol,wet)
 # Open cubicle entrance: side panels only for this layout stage.
for n,x in [('Women',8.25),('Men',13.1)]:box(n+'_Basin',x,13.8,.72,.5,.4,.16,white,wet)
box('Urinal',13.3,15.5,.5,.4,.35,.6,white,wet);box('Urinal_privacy',12.95,15.4,0,.06,.65,1.5,petrol,wet)
box('Cleaning_cupboard',13.2,11.3,0,.5,1,2,petrol,wet)
for n,body,x,d in [('hall','SIX TABLE WAITING HALL',.8,9.75),('coffee','STAFF PREPARATION',1.3,13.7),('court','ARRIVAL COURT',5.25,16.5),('wc','SCREENED HALL',10.2,12.4)]:text(n,body,x,d,.025,.20)
routes={
 'Arrival_to_platform':[(7,16.8),(7,10.8),(7,.1)],
 'Coffee_queue':[(7,9.7),(3,9.7),(2.5,10.2)],
 'Restroom_hall':[(7,9.7),(9,9.7),(9,12.4),(11.7,12.4)],
 'Women_basin':[(9,12.4),(10.45,12.4),(10.45,14.6),(8.9,14.6)],
 'Men_basin':[(11.7,12.4),(12.45,12.4),(12.45,14.5),(13,14.65)],
 'Staff_entry':[(6,14.5),(4.6,14.5),(2,14.5),(2,12)],
 'Locker_approach':[(7,9.7),(12,9.7)]}
for n,pts in routes.items():path(n,[(x,-d,.032) for x,d in pts])
# Conservative horizontal clearance samples against authored solid proxies.
checks=[]
for n,pts in routes.items():
 bad=[]
 for a,b in zip(pts,pts[1:]):
  count=max(2,math.ceil(math.dist(a,b)/.1))
  for i in range(count+1):
   x=a[0]+(b[0]-a[0])*i/count;d=a[1]+(b[1]-a[1])*i/count
   for bn,x0,d0,x1,d1,z0,z1 in blockers:
    if x+.34>x0 and x-.34<x1 and d+.34>d0 and d-.34<d1 and z1>.15 and z0<1.9:bad.append(bn)
 checks.append({'route':n,'radius_m':.34,'blocked_by':sorted(set(bad))})
roof.hide_render=True;roof.hide_viewport=True
def camera(n,pos,target,ortho=None):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=23
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
def light(pos,power,size):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
light((6,-7,11),2200,12);light((1,-14,7),900,8)
s.world=bpy.data.worlds.new('Layout_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.22,.26,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100
views=[camera('01_Plan',(7,-8.6,32),(7,-8.6,0),24.5),camera('02_Cutaway',(24,-32,27),(7,-8,0),27),camera('03_Player_entry',(7,-10.5,1.7),(7,-3,1.5)),camera('04_Coffee_prep',(4.35,-14.5,1.7),(.8,-13,1.3)),camera('05_Restroom_hall',(9,-11.6,1.7),(11,-12.4,1.5))]
s.camera=views[1]
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
# A separate context scene preserves the source route corridors, never moves them.
site=bpy.data.scenes.new('02_Protected_Site_Study');site.unit_settings.system='METRIC';site.world=s.world
context=bpy.data.collections.new('Source_VF07_Routes_and_Anchors');site.collection.children.link(context)
layout=json.loads((REPO/'art/blender/visual_fidelity_07/layout.json').read_text())
for n,(lo,hi) in layout['anchors'].items():box('Reference_'+n,lo[0],-hi[1],lo[2],hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],gray,context,False)
for r in layout['routes']:
 if any(k in r['name'].lower() for k in ['arrival','forest','approach']):path('PROTECT_'+r['name'],r['points'],route,.6,context)
text('Site_note','SOURCE ROUTES: KEEP FIXED / LODGE SITE TRANSFORM NOT COMMITTED',-32,-15,5,.5,True,context)
# No guessed new building placement is saved into the station context.
report={'stage':'Layout blockout only','units':'metres','hall_m':[14,11.2],'gross_area_m2':217.8,'tables':6,'benches':12,'lockers':12,'routes':checks,'site_placement':'uncommitted; protected VF07 routes stored in separate scene','roof':'hidden review envelope','source':str(REPO/'art/blender/visual_fidelity_07/layout.json')}
(OUT/'layout_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Layout.blend'))
for cam in views:
 s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
s.camera=views[1];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Layout.blend'))
