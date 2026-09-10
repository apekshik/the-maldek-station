"""PLK authored metre-scale assets; source remains immutable. Run with Blender 5."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]; SRC=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
HASH=hashlib.sha256(SRC.read_bytes()).hexdigest(); assert HASH=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s;s.name='PLK_Fitted_Review'
# Keep only active-scene context, explicitly outside the asset collection.
# Other source scenes retained as reference-only.
ref=bpy.data.collections.new('REFERENCE_ONLY_Source_Context');s.collection.children.link(ref)
for c in list(s.collection.children):
 if c!=ref:s.collection.children.unlink(c);ref.children.link(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o);ref.objects.link(o)
bpy.context.view_layer.update()
print('Context linked',flush=True)
ref['export']=False
ref.hide_viewport=True
for o in list(s.objects):o['PLK_reference_only']=True
assets=bpy.data.collections.new('PLK_Assets');s.collection.children.link(assets)
review=bpy.data.collections.new('PLK_REVIEW_ONLY');s.collection.children.link(review);review['export']=False
root=bpy.data.objects.new('PLK_Assembly',None);assets.objects.link(root);root.location=(-24.1,4,4);root['coordinate_basis']='local (x,-depth,z) metres; station translation (-24.1,4,4)'
replaced=['FIT_Serving_counter','FIT_Coffee_equipment_run','FIT_Rear_prep_run','FIT_Dry_store','FIT_Urn_Proxy','FIT_Kettle_Proxy','FIT_Wash_sink_Proxy','FIT_Hand_basin_Proxy','FIT_Microwave_Proxy','FIT_Fridge_proxy','FIT_Public_lost_property_cubby','FIT_Menu_placeholder']
survey=[]
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
for n in replaced:
 o=bpy.data.objects[n];survey.append({'name':n,'bounds_world':bounds(o),'matrix_world':[list(r) for r in o.matrix_world]});bpy.data.objects.remove(o,do_unlink=True)
for c in bpy.data.collections:
 if c.name in ['PL03_Removable_Roof']:c.hide_render=True;c.hide_viewport=True
# Source layout annotations and original review rigs are not fitted assets.
for o in list(ref.all_objects):
 if o.type in {'CAMERA','LIGHT','FONT','CURVE'}:o.hide_render=True

def material(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new('PLK_'+n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*c,1);return m
steel=material('Brushed_stainless',(.48,.53,.55),.8,.3)
chrome=material('Chrome',(.65,.7,.72),.95,.19)
black=material('Bakelite_rubber',(.016,.019,.017),0,.32)
inside=material('Carcass_birch',(.42,.31,.18),0,.65)
laminate=material('Warm_grey_laminate',(.3,.32,.29),0,.42)
chalk=material('Chalk_lettering',(.8,.78,.65),0,.75)
paper=material('Paper',(.67,.58,.39),0,.85)
red=material('Red_index',(.35,.055,.025),0,.4)
blue=bpy.data.materials['VF06_Petrol_paint'];cream=bpy.data.materials['VF06_Warm_enamel'];wood=bpy.data.materials['PL03_Aged_Pine'];porcelain=bpy.data.materials['PL03_Warm_Porcelain']
glass=material('Display_glass',(.72,.85,.84),0,.12);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
moving=[];groups={};cur=None

def empty(n,pos=(0,0,0),angle=0,parent=root):
 o=bpy.data.objects.new('PLK_'+n,None);assets.objects.link(o);o.parent=parent;o.location=pos;o.rotation_euler.z=angle;return o

def group(n,x,d,z=0,angle=0):
 global cur
 print('Building '+n,flush=True)
 cur=empty(n,(x,-d,z),angle);groups[n]=cur;return cur

def link(o,n,m,parent=None):
 o.name='PLK_'+n
 for c in list(o.users_collection):c.objects.unlink(o)
 assets.objects.link(o);o.parent=parent or cur;o.data.materials.append(m);return o

def box(n,pos,size,m,parent=None,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1);o=link(bpy.context.object,n,m,parent);o.location=pos;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Manufactured_edge_radius','BEVEL');mod.width=min(b,min(size)/3);mod.segments=3
  mod=o.modifiers.new('Corner_normals','WEIGHTED_NORMAL')
 return o

def cyl(n,pos,r,h,m,parent=None,rot=None,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=r,radius2=r if r2 is None else r2,depth=h);o=link(bpy.context.object,n,m,parent);o.location=pos
 if rot:o.rotation_euler=rot
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 mod=o.modifiers.new('Rolled_edge','BEVEL');mod.width=min(.0015,h/8);mod.segments=2
 return o

def tube(n,pts,r,m,parent=None):
 cu=bpy.data.curves.new('PLK_'+n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new('PLK_'+n,cu);assets.objects.link(o);o.parent=parent or cur;cu.materials.append(m);return o

def label(n,body,pos,size=.035,parent=None,rot=(math.pi/2,0,math.pi),m=chalk):
 cu=bpy.data.curves.new('PLK_'+n,'FONT');cu.body=body;cu.size=size;cu.extrude=.0003;cu.align_x='CENTER';o=bpy.data.objects.new('PLK_'+n,cu);assets.objects.link(o);o.parent=parent or cur;o.location=pos;o.rotation_euler=rot;cu.materials.append(m);return o

def handle(n,u,v,z,w=.12,parent=None):
 return tube(n,[(u-w/2,v,z-.013),(u-w/2,v+.027,z),(u+w/2,v+.027,z),(u+w/2,v,z-.013)],.006,chrome,parent)

def hinge(n,pos,angle=100):
 o=empty(n,pos,parent=cur);o['motion']='hinge';o['axis']='local Z';o['closed_degrees']=0;o['open_degrees']=angle;moving.append(o);return o

def carcass(n,w,dep=.62,h=.865,doors=True,drawers=False):
 # Front is y=0. Rear negative Y. 18 mm sides, recessed toe and 3 mm leaf gaps.
 box(n+'_Toe',(w/2,-dep/2,.065),(w-.06,dep-.1,.13),black)
 for x in [.009,w-.009]:box(n+'_Side',(x,-dep/2,(h+.13)/2),(.018,dep,h-.13),inside)
 box(n+'_Back',(w/2,-dep+.009,(h+.13)/2),(w-.036,.018,h-.13),inside)
 for z in [.14,.47]:box(n+'_Shelf',(w/2,-dep/2,z),(w-.036,dep-.04,.018),inside)
 for y in [-.06,-dep+.04]:box(n+'_Top_rail',(w/2,y,h-.025),(w-.036,.07,.045),inside)
 if not doors:return
 if drawers:
  for j in range(3):
   z=.26+j*.238;p=empty(n+'_Drawer_slide_'+str(j),(0,0,0),parent=cur);p['motion']='slide';p['axis']='local +Y';p['open_metres']=.38;moving.append(p)
   box(n+'_Drawer_front_'+str(j),(w/2,.014,z),(w-.006,.024,.23),blue,p)
   box(n+'_Drawer_bottom_'+str(j),(w/2,-.255,z-.093),(w-.075,.5,.015),inside,p)
   for x in [.045,w-.045]:box(n+'_Drawer_side_'+str(j),(x,-.25,z-.025),(.015,.5,.15),inside,p)
   box(n+'_Drawer_back_'+str(j),(w/2,-.492,z-.025),(w-.075,.015,.15),inside,p);handle(n+'_Pull_'+str(j),w/2,.03,z+.025,parent=p)
 else:
  count=2 if w>.65 else 1
  for j in range(count):
   dw=w/count;left=j*dw+.003;right=(j+1)*dw-.003;hp=hinge(n+'_Door_'+str(j)+'_Pivot',(left,0,.14))
   box(n+'_Door_'+str(j),((right-left)/2,.014,(h-.15)/2),(right-left,.024,h-.15),blue,hp)
   handle(n+'_Pull_'+str(j),right-left-.07,.03,h-.29,parent=hp,w=.075)
   for z in [.12,h-.28]:cyl(n+'_Hinge_barrel',(0,0,z),.006,.045,chrome,hp)

def top(n,w,dep=.65):return box(n+'_Worktop',(w/2,-dep/2,.8825),(w,dep,.035),laminate,b=.006)
# Fixed hatch/counter occupies exactly the old public projection and aperture.
group('Serving',4,11.5,angle=math.pi)
carcass('Serving',3,.63,.965,doors=False)
# Counter panel owns the public face; no added masonry below hatch.
box('Serving_Public_panel',(1.5,-.621,.53),(3,.018,.87),wood)
box('Serving_Public_kick',(1.5,-.623,.06),(3,.022,.12),blue)
box('Serving_Slab',(1.5,-.325,.98),(3,.65,.04),laminate,b=.006)
for x in [.018,1,2,2.982]:box('Serving_Face_stile',(x,-.64,.53),(.032,.012,.86),wood)
# Staff storage: drawer bank and open shelving divided into real bays.
for x in [.6,1.8,2.4]:box('Serving_Divider',(x,-.3,.52),(.018,.56,.76),inside)
for i in range(2):
 z=.38+i*.26;p=empty('Serving_Drawer_'+str(i),(0,0,0),parent=cur);p['motion']='slide';p['axis']='local +Y';p['open_metres']=.35;moving.append(p)
 box('Serving_Drawer_front',(.3,.013,z),(.585,.024,.25),blue,p);box('Serving_Drawer_base',(.3,-.27,z-.10),(.55,.53,.018),inside,p);handle('Serving_Drawer_pull',.3,.03,z+.02,parent=p)
 for x in [.03,.57]:box('Serving_Drawer_side',(x,-.27,z-.025),(.018,.53,.15),inside,p)
 box('Serving_Drawer_back',(.3,-.52,z-.025),(.55,.018,.15),inside,p)
# No jamb/head liner: existing partition owns them; board is in front of head.
group('Menu',2.5,10.99,2.53)
box('Menu_Board',(0,0,0),(2.1,.025,.39),black)
for x in [-1.06,1.06]:box('Menu_Frame',(x,.002,0),(.04,.035,.43),wood)
for z in [-.215,.215]:box('Menu_Frame',(0,.002,z),(2.16,.035,.04),wood)
label('Menu_Editable','COFFEE   /   TEA   /   SNACKS',(0,.019,-.035),.115)
# West run: dry/hot equipment and washing; separate modules.
for n,d,w,drawers in [('Hot_base',12,1.1,False),('Prep_drawers',13.1,.65,True),('Wash_base',13.75,1.2,False)]:
 group(n,.95,d,angle=-math.pi/2);carcass(n,w,.68,drawers=drawers);top(n,w,.7)
 box(n+'_Upstand',(w/2,-.68,1.00),(w,.025,.2),steel)
# rear run explicitly leaves fridge bay (no carcass or toe panel behind fridge).
for n,x,w in [('Rear_left',1.05,1.15),('Rear_right',2.96,1.59)]:
 group(n,x,15.3);carcass(n,w);top(n,w)
group('Rear_bridge',2.2,15.3);top('Rear_bridge',.76)
box('Rear_Upstand',(1.75,-.636,1.0),(3.5,.025,.2),steel,parent=groups['Rear_left'])
# Rounded rectangular bowl cross-section, including underside and open drain.
def roundrect(w,d,r,z,N=8):
 pts=[]
 for cx,cy,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for j in range(N):
   t=math.radians(a+j*90/N);pts.append((cx+r*math.cos(t),cy+r*math.sin(t),z))
 return pts

def bowl(n,w,d,dep):
 rings=[roundrect(w,d,.055,0),roundrect(w-.045,d-.045,.05,-.008),roundrect(w-.09,d-.09,.06,-dep+.035)]
 N=32
 rings.append([(.021*math.cos(2*math.pi*j/N+math.pi/4),.021*math.sin(2*math.pi*j/N+math.pi/4),-dep) for j in range(N)])
 rings.append([(x,y,z-.003) for x,y,z in rings[-1]])
 rings.extend([[(x,y,z-.003) for x,y,z in ring] for ring in rings[2::-1]])
 verts=[p for ring in rings for p in ring];faces=[]
 for k in range(len(rings)):
  for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,((k+1)%len(rings))*N+(j+1)%N,((k+1)%len(rings))*N+j))
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('PLK_'+n,me);assets.objects.link(o);o.parent=cur;me.materials.append(steel)
 for p in me.polygons:p.use_smooth=True
 # Drain strainer ring and separated radial bars above the through-hole.
 cyl(n+'_Waste_neck',(0,0,-dep-.025),.026,.042,black)
 for j in range(4):
  a=j*math.pi/4;tube(n+'_Drain_grid',[(-.022*math.cos(a),-.022*math.sin(a),-dep+.003),(.022*math.cos(a),.022*math.sin(a),-dep+.003)],.0013,steel)
 return o

def tap(n,x,y,z):
 cyl(n+'_Foot',(x,y,z+.012),.024,.024,chrome)
 pts=[(x,y,z+.02),(x,y,z+.18)]
 for j in range(13):
  a=math.pi-j*math.pi/12;pts.append((x+.075+.075*math.cos(a),y,z+.18+.075*math.sin(a)))
 pts.append((x+.15,y,z+.15));tube(n+'_Swan_neck',pts,.009,chrome)
 cyl(n+'_Aerator',(x+.15,y,z+.15),.013,.018,chrome)
 for yy,col in [(y-.06,red),(y+.06,blue)]:
  cyl(n+'_Valve',(x,yy,z+.035),.015,.065,chrome);tube(n+'_Cross',[(x-.026,yy,z+.065),(x+.026,yy,z+.065)],.004,chrome);tube(n+'_Cross',[(x,yy-.026,z+.065),(x,yy+.026,z+.065)],.004,chrome);cyl(n+'_Index',(x,yy,z+.069),.006,.004,col)
# Sink cutout removes full worktop thickness. Boolean cutter is never exported.
group('Wash_sink',.565,14.58,.905);bowl('Wash_Bowl',.51,.61,.205);tap('Wash_Tap',-.195,0,0)
bpy.context.view_layer.update()
work=bpy.data.objects['PLK_Wash_base_Worktop']
cut=box('TEMP_sink_cutout',(0,0,-.07),(.472,.572,.3),black,b=.04)
bpy.context.view_layer.update();bpy.context.view_layer.objects.active=cut
for mod in list(cut.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
mod=work.modifiers.new('Actual_sink_aperture','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';bpy.context.view_layer.objects.active=work;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Drainer ahead of wash bowl, not behind an uncut slab.
box('Wash_Drainer',(0,.47,.001),(.5,.28,.006),steel)
for j in range(7):box('Wash_Drainer_rib',(-.205+j*.068,.47,.006),(.01,.23,.005),steel,b=.002)
# Separate handwash point, mounted off the west wall beyond the run.
group('Hand_basin',4.46,13.24,.86,angle=math.pi);bowl('Hand_Bowl',.46,.37,.14);tap('Hand_Tap',-.17,0,0)
for y in [-.12,.12]:tube('Hand_Bracket',[(-.31,y,-.02),(-.31,y,-.3),(.1,y,-.02)],.012,steel)
tube('Hand_Waste',[(0,0,-.155),(0,0,-.39),(-.10,0,-.44),(-.22,0,-.39),(-.22,0,-.25),(-.32,0,-.25)],.018,chrome)
box('Hand_Splash_back',(-.323,0,.16),(.018,.55,.4),steel)
box('Hand_Splash_separator',(0,.265,.18),(.66,.018,.38),steel)
box('Hand_Soap',(-.28,-.28,.22),(.09,.11,.16),cream)
box('Hand_Towel_dispenser',(-.28,0,.62),(.10,.30,.22),cream)
label('Handwash_label','HAND WASH',(-.222,0,.39),.033,rot=(math.pi/2,0,math.pi/2))
# Urn: rolled vessel, lid, handles, sight gauge, mechanical thermostat, lever tap.
group('Urn',.56,12.37,.9)
cyl('Urn_Base',(0,0,.05),.17,.1,black)
cyl('Urn_Vessel',(0,0,.267),.163,.35,steel)
for z in [.095,.442]:cyl('Urn_Rolled_band',(0,0,z),.168,.012,chrome)
p=empty('Urn_Lid_lift',(0,0,.451),parent=cur);p['motion']='lift';p['axis']='local +Z';p['open_metres']=.15;moving.append(p)
cyl('Urn_Lid',(0,0,.003),.17,.018,steel,p,r2=.16);cyl('Urn_Lid_knob',(0,0,.034),.029,.035,black,p)
for y in [-.185,.185]:tube('Urn_Carry_handle',[(-.055,y*.88,.35),(-.055,y,.36),(.055,y,.36),(.055,y*.88,.35)],.013,black)
tube('Urn_Spout',[(.15,0,.155),(.235,0,.155),(.245,0,.125)],.014,chrome)
cyl('Urn_Tap_valve',(.215,0,.18),.019,.05,chrome);tube('Urn_Tap_lever',[(.215,0,.2),(.215,0,.255)],.012,black)
cyl('Urn_Dial',(.172,-.07,.065),.027,.02,black,rot=(0,math.pi/2,0))
box('Urn_Level_gauge',(.165,.066,.28),(.013,.025,.23),cream);tube('Urn_Gauge_glass',[(.177,.066,.18),(.177,.066,.37)],.004,chrome)
for z in [.21,.25,.29,.33,.37]:box('Urn_Gauge_mark',(.179,.066,z),(.002,.015,.0015),black)
box('Urn_Drip_tray',(.282,0,.012),(.2,.25,.024),black)
for j in range(8):box('Urn_Drip_grate',(.282,-.1+j*.028,.027),(.17,.009,.008),steel)
# K2-inspired bell silhouette using a revolved profile; separate lid and arched handle.
def lathe(n,profile,m):
 N=64;verts=[]
 for r,z in profile:
  verts.extend([(r*math.cos(j*2*math.pi/N),r*math.sin(j*2*math.pi/N),z) for j in range(N)])
 faces=[]
 for k in range(len(profile)-1):
  for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 faces.extend([tuple(range(N-1,-1,-1)),tuple((len(profile)-1)*N+j for j in range(N))]);me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('PLK_'+n,me);assets.objects.link(o);o.parent=cur;me.materials.append(m)
 for p in me.polygons:p.use_smooth=len(p.vertices)==4
 return o
group('Kettle',.55,13.02,.9)
lathe('Kettle_Bell',[(.11,.009),(.118,.03),(.116,.085),(.1,.16),(.072,.205),(.065,.215)],steel)
cyl('Kettle_Base',(0,0,.009),.111,.017,black)
p=empty('Kettle_Lid_lift',(0,0,.218),parent=cur);p['motion']='lift';p['axis']='local +Z';p['open_metres']=.09;moving.append(p)
cyl('Kettle_Lid',(0,0,0),.068,.009,chrome,p,r2=.061);cyl('Kettle_Lid_knob',(0,0,.018),.018,.028,black,p)
tube('Kettle_Handle',[(-.087,0,.15)]+[(.12*math.cos(math.pi-j*math.pi/24),0,.17+.14*math.sin(math.pi-j*math.pi/24)) for j in range(25)]+[(.09,0,.155)],.014,black)
# Tapered hollow spout: open mouth, inner ring and closed attachment.
pts=[(.09,-.025,.105),(.18,-.035,.185)]
a=Vector(pts[0]);b=Vector(pts[1]);o=cyl('Kettle_Spout',(a+b)/2,.031,(b-a).length,steel,r2=.019);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
cyl('Kettle_Spout_mouth',b,.014,.002,black,rot=tuple(o.rotation_euler))
box('Kettle_Switch',(-.115,0,.06),(.025,.022,.037),black)
tube('Kettle_Cord',[(-.115,0,.04),(-.18,.05,.015),(-.22,.2,.012),(-.30,.2,.02)],.004,black)
# Microwave, shell panels enclose an actual cavity. Door faces +Y.
group('Microwave',1.55,15.38,.923)
w=.51;dep=.43;h=.306
for x in [.012,w-.012]:box('Microwave_Side',(x,-dep/2,h/2),(.024,dep,h),cream)
for z in [.012,h-.012]:box('Microwave_Shell',(w/2,-dep/2,z),(w-.048,dep,.024),cream)
box('Microwave_Back',(w/2,-dep+.012,h/2),(w-.048,.024,h-.048),steel)
box('Microwave_Cavity_floor',(.213,-.21,.033),(.36,.35,.015),porcelain)
box('Microwave_Control_block',(.465,-.05,h/2),(.07,.12,h-.048),cream)
p=hinge('Microwave_Door_Pivot',(.015,.005,.02),95)
box('Microwave_Door',(.20,.015,.132),(.40,.032,.267),black,p)
box('Microwave_Window',(.175,.032,.138),(.29,.005,.183),steel,p)
# Real grille bars in front of recessed dark window; no branded graphic.
box('Microwave_Window_dark',(.175,.036,.138),(.28,.002,.171),black,p)
for j in range(18):box('Microwave_Screen_bar',(.038+j*.016,.038,.138),(.002,.001,.17),steel,p,b=0)
tube('Microwave_Handle',[(.367,.033,.07),(.367,.06,.08),(.367,.06,.21),(.367,.033,.22)],.009,black,p)
for z in [.092,.225]:
 cyl('Microwave_Timer',(.465,.018,z),.025,.023,black,rot=(math.pi/2,0,0));box('Microwave_Dial_index',(.465,.032,z+.013),(.003,.002,.012),chalk)
 for j in range(12):
  a=j*math.pi/6;box('Microwave_Dial_tick',(.465+.035*math.sin(a),.012,z+.035*math.cos(a)),(.002,.002,.005),black)
for j in range(8):box('Microwave_Side_vent',(w+.0005,-.16-j*.022,.23),(.002,.011,.045),black)
for x in [.05,.46]:
 for y in [-.05,-.37]:cyl('Microwave_Foot',(x,y,-.012),.016,.024,black)
label('Microwave_Control_text','TIME',(.465,.033,.163),.012,m=black)
# Small fridge in its own 760 mm opening.
group('Fridge',2.28,15.32,.035)
w=.6;dep=.57;h=.815
for x in [.024,w-.024]:box('Fridge_Side',(x,-dep/2,h/2),(.048,dep,h),cream)
for z in [.035,h-.025]:box('Fridge_Shell',(w/2,-dep/2,z),(w-.096,dep,.05),cream)
box('Fridge_Back',(w/2,-dep+.035,h/2),(w-.096,.07,h-.1),cream)
for z in [.21,.4,.59]:
 box('Fridge_Shelf',(w/2,-.28,z),(w-.11,.43,.012),porcelain)
 for x in [.07,.53]:box('Fridge_Shelf_support',(x,-.28,z-.01),(.012,.42,.025),cream)
p=hinge('Fridge_Door_Pivot',(.012,.005,.055),100)
box('Fridge_Door',(.285,.015,.355),(.582,.052,.712),cream,p,b=.018)
for x in [.02,.55]:box('Fridge_Gasket',(x,-.02,.35),(.012,.014,.68),black,p)
for z in [.016,.687]:box('Fridge_Gasket',(.285,-.02,z),(.53,.014,.012),black,p)
handle('Fridge_Pull',.515,.045,.54,.10,p)
for z in [.16,.39]:box('Fridge_Inner_rack',(.285,-.08,z),(.47,.1,.05),cream,p)
for x in [.07,.53]:
 for y in [-.06,-.5]:cyl('Fridge_Foot',(x,y,-.018),.024,.034,black)
for j in range(13):box('Fridge_Vent',(.06+j*.04,.003,.025),(.022,.012,.018),black)
# Dry shelving: open access faces kitchen (south), behind original proxy frontage.
group('Dry_store',4.5,12.15,angle=math.pi)
for x in [.018,1.032]:
 for y in [-.018,-.532]:box('Dry_Post',(x,y,1.05),(.035,.035,2.1),blue)
for z in [.15,.55,.95,1.35,1.75,2.08]:box('Dry_Shelf',(.525,-.275,z),(1.05,.55,.025),inside)
tube('Dry_Diagonal',[(.02,-.53,.2),(1.03,-.53,2.02)],.009,steel)
for j in range(3):
 for k in range(2):
  box('Dry_Paper_pack',(.18+j*.30,-.22,.69+k*.8),(.21,.28,.25),paper,b=.008)
label('Dry_Label','DRY STORES',(.52,.009,1.82),.057)
# Public cubby maintains source envelope and opens toward hall.
group('Lost_property',4.22,10.6,.65)
for x in [.009,.491]:box('Cubby_Side',(x,-.2,.275),(.018,.4,.55),wood)
for z in [.009,.275,.541]:box('Cubby_Shelf',(.25,-.2,z),(.464,.4,.018),wood)
box('Cubby_Back',(.25,-.39,.275),(.464,.02,.514),wood)
label('Cubby_Label','LOST PROPERTY',(.25,.003,.49),.038)
box('Cubby_Folded_scarf',(.2,-.21,.04),(.25,.18,.045),blue,b=.014)
# Restrained tabletop dressing, no invented evidence.
group('Dressing',0,0)
def cup(n,x,d,z):
 global cur
 group(n,x,d,z)
 lathe(n+'_Ceramic',[(.028,0),(.035,.008),(.042,.085),(.038,.089),(.034,.081),(.029,.012)],porcelain)
 tube(n+'_Handle',[(.036+.027*math.sin(j*math.pi/16),0,.047+.025*math.cos(j*math.pi/16)) for j in range(17)],.006,porcelain)
 cyl(n+'_Saucer',(0,0,-.005),.065,.009,porcelain)
for j in range(4):cup('Cup_'+str(j),1.28+j*.15,11.28,1.014)
group('Tray',1.52,11.24,1.0)
box('Service_Tray',(0,0,.012),(.72,.39,.016),steel)
for x in [-.36,.36]:box('Tray_Lip',(x,0,.025),(.012,.39,.025),steel)
for y in [-.195,.195]:box('Tray_Lip',(0,y,.025),(.72,.012,.025),steel)
# Containers at rear leave ~1.2 m of continuous preparation worktop clear.
for j,body in enumerate(['TEA','COFFEE','SUGAR']):
 group('Tin_'+body,3.75+j*.22,15.75,.9);cyl('Tin_'+body,(0,0,.08),.075,.16,cream);cyl('Tin_Lid_'+body,(0,0,.166),.078,.012,blue);label('Tin_Text_'+body,body,(0,.076,.065),.026,m=black)
group('Snack_display',3.32,11.14,1.0)
box('Snack_Tray',(0,0,.013),(.62,.38,.026),wood)
for x in [-.31,.31]:box('Snack_Glass_side',(x,0,.15),(.006,.37,.27),glass)
box('Snack_Glass_front',(0,.186,.15),(.614,.006,.27),glass)
box('Snack_Glass_top',(0,0,.288),(.626,.38,.006),glass)
for i in range(3):
 for j in range(2):box('Snack_Wrapped_biscuit',(-.2+i*.19,-.085+j*.16,.053),(.15,.11,.054),paper,b=.012)
label('Snack_Sign','BISCUITS',(0,.194,.08),.035,m=black)
group('Waste_bin',4.48,12.62)
lathe('Waste_bin_body',[(.15,.015),(.17,.04),(.185,.49),(.175,.495),(.16,.05)],blue)
cyl('Waste_bin_lid',(0,0,.505),.19,.024,black);box('Waste_bin_pedal',(0,.19,.025),(.12,.08,.025),black)
# Shelf on west wall above free prep area, with functional brackets and crockery.
group('Wall_shelf',.21,13.22,1.63,angle=-math.pi/2)
box('Wall_shelf_board',(.55,.17,0),(1.1,.34,.025),wood)
for x in [.1,1.0]:tube('Shelf_Bracket',[(x,.01,-.25),(x,.01,-.02),(x,.30,-.02),(x,.01,-.25)],.009,steel)
for j in range(6):cyl('Stacked_saucer',(.3,.15,.024+j*.011),.075,.009,porcelain)
# Review rigs use neutral temporary area lights.
for n,pos,power,size in [('Ceiling',(-21.6,-9.5,7.0),450,4),('Hall',(-21.8,-5.7,6.8),400,3),('Fill',(-20,-10.4,6.7),220,2)]:
 d=bpy.data.lights.new('PLK_REVIEW_'+n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=pos
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('PLK_REVIEW_Neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.55,.6,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.view_settings.view_transform='AgX'
views=[('01_Customer', (2.5,8.35,1.65),(2.5,11.65,1.23),30),('02_Staff_counter',(2.6,13.4,1.65),(2.4,11.05,1.08),28),('03_Staff_entry',(4.55,14.5,1.65),(.65,13.3,1.07),24),('04_Rear_prep',(2.9,13.18,1.65),(2.7,15.65,1.05),28),('05_Washing',(1.72,14.08,1.65),(.45,14.58,.90),26),('06_Overhead',(2.5,13.2,8.5),(2.5,13.2,0),35)]
for n,pos,target,lens in views:
 d=bpy.data.cameras.new('PLK_REVIEW_'+n);o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=Vector((pos[0]-24.1,4-pos[1],4+pos[2]));tar=Vector((target[0]-24.1,4-target[1],4+target[2]));o.rotation_euler=(tar-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.035
 if 'Overhead' in n:d.type='ORTHO';d.ortho_scale=7.2
s.camera=bpy.data.objects['PLK_REVIEW_03_Staff_entry']
bpy.context.view_layer.update()
# Convert capped tubes and weld their cap rings, applying all mesh modifiers for stable QA.
for o in list(assets.all_objects):
 if o.type not in {'MESH','CURVE'}:continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# All source-relative transforms, slots and articulated components are discoverable.
bpy.context.view_layer.update()
records=[]
for o in assets.all_objects:
 records.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'dimensions':list(o.dimensions),'matrix_world':[list(r) for r in o.matrix_world],'location_parent':list(o.location),'rotation_parent_radians':list(o.rotation_euler),'materials':[m.name for m in o.data.materials] if o.type in {'MESH','FONT'} else [],'motion':dict(o.items()) if o in moving else None})
mp={'FIT_Serving_counter':['Serving'],'FIT_Coffee_equipment_run':['Hot_base','Prep_drawers','Wash_base','Wall_shelf'],'FIT_Rear_prep_run':['Rear_left','Rear_right','Rear_bridge'],'FIT_Dry_store':['Dry_store'],'FIT_Urn_Proxy':['Urn'],'FIT_Kettle_Proxy':['Kettle'],'FIT_Wash_sink_Proxy':['Wash_sink'],'FIT_Hand_basin_Proxy':['Hand_basin'],'FIT_Microwave_Proxy':['Microwave'],'FIT_Fridge_proxy':['Fridge'],'FIT_Public_lost_property_cubby':['Lost_property'],'FIT_Menu_placeholder':['Menu']}
manifest={'source':str(SRC),'source_sha256':HASH,'assembly_translation':[-24.1,4,4],'units':'metres Z up; local Y=-depth','replacements':[dict(r,new_roots=['PLK_'+q for q in mp[r['name']]]) for r in survey],'wall_patch':None,'surface_ownership':'Existing partition owns unlined jamb/head; PLK counter owns low aperture closure, slab and cabinetry. No duplicate sill/core. Staff door reserved to PLD.','objects':records,'views':views,'reference_export_exclusions':['REFERENCE_ONLY_Source_Context','PLK_REVIEW_ONLY'],'remaining':'Unreal export/collision/material baking/interaction and services are later integration.'}
(OUT/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'material_manifest.json').write_text(json.dumps([{'name':m.name,'procedural_blender_only':len(m.node_tree.nodes)>2 if m.use_nodes else False} for m in set(m for o in assets.all_objects if o.type in {'MESH','FONT'} for m in o.data.materials)],indent=2))
ref.hide_viewport=False
# Friendly fitted viewport.
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_distance=7;a.spaces.active.region_3d.view_location=(-21.6,-9.5,5);a.spaces.active.clip_end=200
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen.blend'))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==HASH
print('PLK BUILD COMPLETE',len(records),flush=True)
