"""Build PLR complete restroom package. Blender 5.0, metres, no master edits."""
import bpy, math, json, hashlib, bmesh
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]; SRC=P.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
SHA=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert SHA=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
for sc in list(bpy.data.scenes):
 if sc!=s:bpy.data.scenes.remove(sc)
s.name='PLR_Fitted_Review'
def coll(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
asset=coll('PLR_Assets');review=coll('PLR_REVIEW_ONLY');ref=coll('PLR_REFERENCE_ONLY')
original=list(s.objects)
source_renderable=set()
def gather_visible(lc,blocked=False):
 blocked=blocked or lc.exclude or lc.collection.hide_render
 if not blocked:source_renderable.update(lc.collection.objects)
 for ch in lc.children:gather_visible(ch,blocked)
gather_visible(s.view_layers[0].layer_collection)
for o in original:
 if o not in source_renderable:
  o.hide_render=True;o.hide_viewport=True;o['source_collection_excluded']=True
 for c in list(o.users_collection):c.objects.unlink(o)
 ref.objects.link(o);o['reference_only']=True
for c in list(s.collection.children):
 if c not in (asset,review,ref):s.collection.children.unlink(c)
# Source annotations/cameras are not authored fixtures.
for o in original:
 if o.type in ('CURVE','FONT','CAMERA','LIGHT') or 'Roof' in o.name or 'roof' in o.name:o.hide_render=True;o.hide_viewport=True
replacements={}
for o in original:
 if o.name in ['FIT_Women_Basin','FIT_Men_Basin','FIT_Urinal','FIT_Urinal_privacy'] or any(o.name.startswith('FIT_'+n+'_') for n in ['Women_A','Women_B','Men_A']):
  replacements[o.name]=[];bpy.data.objects.remove(o,do_unlink=True)
def mat(n,c,rough=.45,metal=0):
 m=bpy.data.materials.new('PLR_'+n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
cream=mat('Vitreous_cream',(.82,.80,.70),.19);seatmat=mat('Seat_ivory',(.66,.65,.55),.3);petrol=mat('Laminate_petrol',(.055,.16,.145),.42);steel=mat('Brushed_chrome',(.5,.55,.55),.24,.85);dark=mat('Rubber_graphite',(.027,.035,.032),.65);mirror=mat('Mirror_silver',(.9,.92,.92),.055,1);white=mat('Paper',(.84,.83,.73),.8);red=mat('Occupied_red',(.45,.035,.02));green=mat('Vacant_green',(.045,.32,.16));gold=mat('Review_swing',(.9,.44,.045))
def W(p):return Vector((p[0]-24.1,4-p[1],p[2]+4))
def link(o,n,m,c=asset):
 o.name='PLR_'+n
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def box(n,p,dim,m,bevel=.008):
 v=[(dx*dim[0]/2,dy*dim[1]/2,dz*dim[2]/2) for dx,dy,dz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 o=mesh(n,v,f,m);o.location=W(p)
 for poly in o.data.polygons:poly.use_smooth=False
 if bevel:
  mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=min(bevel,min(dim)*.4);mod.segments=3
 return o
def tube(n,pts,r,m):
 # Closed swept mesh with shared cap vertices (avoids disconnected curve caps).
 pts=[W(p) for p in pts];verts=[];N=24
 spread=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)];seed=Vector(tuple(1 if i==spread.index(min(spread)) else 0 for i in range(3)))
 for i,p in enumerate(pts):
  t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();a=t.cross(seed)
  if a.length<.01:a=t.cross(Vector((0,1,0)))
  a.normalize();b=t.cross(a).normalized()
  verts += [p+r*(a*math.cos(j*2*math.pi/N)+b*math.sin(j*2*math.pi/N)) for j in range(N)]
 faces=[tuple(reversed(range(N))),tuple((len(pts)-1)*N+j for j in range(N))]
 for i in range(len(pts)-1):
  for j in range(N):k=(j+1)%N;faces.append((i*N+j,i*N+k,(i+1)*N+k,(i+1)*N+j))
 return mesh(n,verts,faces,m)
def mesh(n,v,f,m):
 me=bpy.data.meshes.new('PLR_'+n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('PLR_'+n,me);asset.objects.link(o);me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 return o
def bowl(n,p,rx,ry,profile,m):
 N=64;v=[W((p[0]+rx*r*math.cos(j*2*math.pi/N),p[1]+ry*r*math.sin(j*2*math.pi/N),p[2]+z)) for r,z in profile for j in range(N)];f=[]
 for i in range(len(profile)):
  k=(i+1)%len(profile)
  for j in range(N):q=(j+1)%N;f.append((i*N+j,i*N+q,k*N+q,k*N+j))
 return mesh(n,v,f,m)
def text(n,body,p,size=.07,rot=(math.pi/2,0,math.pi),m=white):
 cu=bpy.data.curves.new('PLR_'+n,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.0005;o=bpy.data.objects.new('PLR_'+n,cu);asset.objects.link(o);o.location=W(p);o.rotation_euler=rot;cu.materials.append(m);return o
def parent(o,p):
 mw=o.matrix_basis.copy();o.parent=p;o.matrix_parent_inverse=Matrix.Translation(-p.location);o.matrix_basis=mw
pivots=[]
def door(n,x,d,w,h,bottom=0.02,side=1,entry=False):
 hinged=d+(.026 if entry else 0)
 pivot=bpy.data.objects.new('PLR_'+n+'_Pivot',None);asset.objects.link(pivot);pivot.location=W((x,hinged,bottom));pivot.empty_display_size=.15
 start=set(asset.objects)
 box(n+'_Leaf',(x+side*w/2,d,bottom+h/2),(w,.036 if not entry else .044,h),petrol if not entry else cream)
 # Kick plates intentionally proud of the leaf on each side.
 for face in [-1,1]:
  if entry:box(n+'_Kickplate_'+str(face),(x+side*w/2,d+face*.024,.21),(w-.07,.003,.25),steel,.002)
  box(n+'_Latch_rose_'+str(face),(x+side*(w-.10),d+face*.026,1.05),(.055,.012,.14),steel,.005)
  tube(n+'_Lever_'+str(face),[(x+side*(w-.10),d+face*.038,1.05),(x+side*(w-.10),d+face*(.07 if entry else .05),1.05),(x+side*(w-.20),d+face*(.07 if entry else .05),1.05)],.012,steel)
 if not entry:
  box(n+'_Indicator_surround',(x+side*(w-.10),d-.038,1.12),(.038,.014,.036),dark,.005)
  box(n+'_Indicator_VACANT',(x+side*(w-.10),d-.046,1.12),(.025,.003,.018),green,.003)
  box(n+'_Slide_bolt',(x+side*(w-.065),d+.032,1.12),(.095,.018,.019),steel,.004)
  tube(n+'_Coat_hook',[(x+side*.18,d+.024,1.73),(x+side*.18,d+.052,1.73),(x+side*.18,d+.052,1.77)],.008,steel)
 for o in set(asset.objects)-start:parent(o,pivot)
 for z in ([.25,1.1,1.98] if entry else [.36,1.70]):
  tube(n+'_Hinge_barrel_'+str(z),[(x,hinged,z-.055),(x,hinged,z+.055)],.012,steel)
  box(n+'_Hinge_fixed_'+str(z),(x-side*.025,d+.017,z),(.04,.02,.105),steel,.003)
  o=box(n+'_Hinge_leaf_'+str(z),(x+side*.03,d+.019,z),(.045,.014,.105),steel,.003);parent(o,pivot)
 box(n+'_Stop',(x+side*(w+.008),d+(-.029 if entry else .029),1.1),(.018,.022,.095),dark,.003)
 if entry:
  o=text(n+'_Sign',n.split('_')[0].upper(),(x+side*w/2,d-.028,1.66),.065,m=petrol);parent(o,pivot)
 # Positive local depth requires negative world angle for +X leaves.
 angle=(-side*(85 if n=='Women_Entry' else 90)) if entry else side*90
 if entry:
  theta=math.radians(abs(angle));sx=x+side*w*math.cos(theta)-side*.027;sd=hinged+w*math.sin(theta)-(.026 if entry else 0)*math.cos(theta)+.014
  tube(n+'_Open_stop',[(sx,sd,.004),(sx,sd,.06)],.018,dark)
 pivot['open_angle_degrees']=angle;pivot['leaf_width_m']=w
 pivot.rotation_euler.z=0;pivot.keyframe_insert(data_path='rotation_euler',frame=1)
 pivot.rotation_euler.z=math.radians(angle);pivot.keyframe_insert(data_path='rotation_euler',frame=40)
 pivot.rotation_euler.z=0
 pivots.append(dict(name=pivot.name,position_world=list(pivot.location),width=w,open_degrees=angle,kind='entrance' if entry else 'stall'))
 pts=[]
 for t in range(49):
  theta=math.radians(angle)*t/48;dx=side*w;dd=d-hinged
  pts.append((x+dx*math.cos(theta)+dd*math.sin(theta),hinged-dx*math.sin(theta)+dd*math.cos(theta),.012))
 o=tube(n+'_REVIEW_sweep',pts,.009,gold);asset.objects.unlink(o);review.objects.link(o);o['review_only']=True
 return pivot
# Entrance reveal liners occupy existing clear edges; patch only concealed boundary strips.
patch=[]
for label,a,side in [('Women',10,-1),('Men',12,-1)]:
 for edge in [a,a+.9]:box(label+'_Entry_jamb_'+str(edge),(edge+(-.009 if edge==a else .009),13.11,1.1),(.018,.21,2.2),steel,.002)
 box(label+'_Entry_head',(a+.45,13.11,2.211),(.936,.21,.022),steel,.002)
 for face_depth in [13.0,13.22]:
  for xx in [a-.03,a+.93]:box(label+'_Entry_face_trim',(xx,face_depth,1.1),(.06,.012,2.2),steel,.002)
  box(label+'_Entry_face_header',(a+.45,face_depth,2.23),(1.02,.012,.06),steel,.002)
 # Clear opening remains nominal 0.900 x 2.200. Liner backs get concealed recess.
 patch.append(dict(opening=label,x=[a,a+.9],depth=[13.02,13.2],z=[0,2.2],recess_m=.022))
 door(label+'_Entry',a+.002 if side==1 else a+.898,13.226,.896,2.16,.02,side,True)
# Recess only the three jamb/core boundaries and heads adjacent to the two openings.
import sys
sys.path.insert(0,str(P/'scripts'))
from opening_patch import apply
changes=apply()
# Cubicles retain the approved 1.20/1.25 x 1.60 envelopes.
for n,x,w in [('Women_A',8.25,1.2),('Women_B',9.6,1.2),('Men_A',11.2,1.25)]:
 before=set(asset.objects)
 for suffix,xx in [('Left',x+.03),('Right',x+w-.03)]:
  panel=box(n+'_'+suffix+'_Partition',(xx,16.1,1.1),(.032,1.6,1.90),petrol)
  replacements['FIT_'+n+'_'+suffix+'_partition']=[panel.name]
  for dd in [15.42,16.74]:
   tube(n+'_'+suffix+'_Foot',[(xx,dd,.025),(xx,dd,.26)],.021,steel)
   box(n+'_'+suffix+'_Foot_plate',(xx,dd,.018),(.09,.09,.026),steel,.005)
  box(n+'_'+suffix+'_Top_rail',(xx,16.1,2.07),(.045,1.62,.055),steel)
 # 0.78 leaf within the pilasters; raised panel baseline is 150 mm.
 hinge=x+.18;end=hinge+.80
 box(n+'_Hinge_pilaster',(x+.09,15.36,1.10),(.14,.04,1.90),petrol)
 box(n+'_Latch_pilaster',((end+x+w-.046)/2,15.36,1.10),(x+w-.046-end,.04,1.90),petrol)
 box(n+'_Front_brace',(x+w/2,15.30,2.07),(w,.045,.055),steel)
 door(n+'_Stall',hinge+.01,15.328,.78,1.85,.15,1)
 # Closed rear panel closes the 120 mm gap to the building back wall without expanding cubicle.
 box(n+'_Rear',(x+w/2,16.884,1.10),(w-.06,.032,1.90),petrol)
 # WC faces the door, cistern at back.
 cx=x+w/2
 bowl(n+'_Toilet_bowl',(cx,16.45,.43),.235,.30,[(.23,-.27),(.55,-.25),(.9,-.13),(1,-.035),(.99,0),(.85,.007),(.74,-.045),(.42,-.18),(.23,-.2)],cream)
 bowl(n+'_Seat',(cx,16.45,.46),.241,.305,[(1,-.015),(1,.012),(.81,.019),(.78,-.01)],seatmat)
 tube(n+'_Bowl_water',[(cx,16.45,.273),(cx,16.45,.275)],.092,dark)
 box(n+'_Pedestal',(cx,16.47,.13),(.25,.36,.26),cream,.075)
 box(n+'_Cistern',(cx,16.765,.66),(.40,.19,.38),cream,.035)
 box(n+'_Cistern_lid',(cx,16.765,.863),(.425,.215,.035),cream,.014)
 box(n+'_Flush_button',(cx+.12,16.66,.75),(.065,.017,.032),steel,.008)
 for xx in [cx-.12,cx+.12]:tube(n+'_Seat_hinge',[(xx,16.66,.45),(xx,16.70,.45)],.018,steel)
 tube(n+'_Supply',[(cx+.24,16.87,.18),(cx+.24,16.80,.18),(cx+.24,16.80,.59)],.009,steel)
 box(n+'_Isolation_valve',(cx+.24,16.80,.25),(.045,.035,.035),steel)
 tube(n+'_Waste_soil',[(cx,16.57,.16),(cx,16.77,.16),(cx,16.81,.12),(cx,16.81,-.01)],.05,cream)
 box(n+'_Paper_dispenser',(x+w-.11,16.18,.86),(.12,.24,.21),steel,.025)
 box(n+'_Paper_tail',(x+w-.177,16.16,.735),(.006,.12,.10),white,.001)
 box(n+'_Sanitary_bin',(x+w-.19,16.61,.23),(.23,.24,.42),cream,.035)
 box(n+'_Bin_lid',(x+w-.19,16.61,.452),(.24,.25,.035),steel)
 replacements['FIT_'+n+'_WC']=[o.name for o in set(asset.objects)-before if any(k in o.name for k in ['Toilet','Seat','Pedestal','Cistern','Flush','Supply','Isolation','Waste'])]
# Wall mounted basins face the room from west/east side walls.
for n,wall,sign in [('Women',8.18,1),('Men',13.82,-1)]:
 before=set(asset.objects);cx=wall+sign*.28;dd=14.18 if n=='Women' else 14.5
 bowl(n+'_Basin_bowl',(cx,dd,.86),.255,.31,[(.11,-.20),(.65,-.19),(.96,-.045),(1,-.01),(.98,.01),(.82,.014),(.72,-.03),(.44,-.13),(.11,-.15)],cream)
 box(n+'_Tap_deck',(wall+sign*.10,dd,.790),(.18,.49,.15),cream,.02)
 tube(n+'_Drain',[(cx,dd,.719),(cx,dd,.737)],.029,steel)
 for j in range(7):
  a=j*math.tau/7;tube(n+'_Drain_slot_'+str(j),[(cx+.016*math.cos(a),dd+.016*math.sin(a),.737),(cx+.016*math.cos(a),dd+.016*math.sin(a),.739)],.0027,dark)
 box(n+'_Overflow',(cx-sign*.189,dd,.819),(.007,.047,.012),dark,.004)
 tube(n+'_Trap',[(cx,dd,.69),(cx,dd,.46),(cx-sign*.07,dd,.40),(cx-sign*.15,dd,.45),(cx-sign*.15,dd,.54),(wall+sign*.02,dd,.54)],.022,steel)
 tube(n+'_Waste_wall_flange',[(wall-sign*.005,dd,.54),(wall+sign*.03,dd,.54)],.037,steel)
 for off in [-.14,.14]:
  tube(n+'_Supply_wall_flange_'+str(off),[(wall-sign*.005,dd+off,.57),(wall+sign*.03,dd+off,.57)],.024,steel)
  tube(n+'_Supply_'+str(off),[(wall+sign*.025,dd+off,.57),(wall+sign*.10,dd+off,.57),(wall+sign*.10,dd+off,.86)],.008,steel)
  box(n+'_Mount_bracket_'+str(off),(wall+sign*.12,dd+off,.68),(.25,.025,.045),steel)
  box(n+'_Valve_'+str(off),(wall+sign*.075,dd+off,.57),(.032,.045,.032),steel)
 tube(n+'_Mixer_spout',[(wall+sign*.10,dd,.85),(wall+sign*.10,dd,1.04),(wall+sign*.18,dd,1.08),(cx,dd,1.04),(cx,dd,.995)],.018,steel)
 box(n+'_Mixer_lever',(wall+sign*.10,dd,1.065),(.09,.025,.018),steel)
 box(n+'_Mirror_frame',(wall+sign*.022,dd,1.52),(.035,.68,.79),steel)
 box(n+'_Mirror',(wall+sign*.042,dd,1.52),(.006,.63,.74),mirror,.002)
 box(n+'_Soap_dispenser',(wall+sign*.075,dd-.49,1.12),(.13,.12,.21),cream,.024)
 box(n+'_Soap_pump',(wall+sign*.145,dd-.49,1.03),(.045,.055,.022),steel)
 box(n+'_Towel_dispenser',(wall+sign*.092,dd+.55,1.29),(.18,.28,.35),steel,.025)
 box(n+'_Towel',(wall+sign*.13,dd+.55,1.065),(.014,.19,.12),white,.001)
 box(n+'_Waste_bin',(wall+sign*.20,dd+(-.56 if n=='Women' else .59),.22),(.30,.32,.42),petrol,.035)
 box(n+'_Waste_bin_rim',(wall+sign*.20,dd+(-.56 if n=='Women' else .59),.44),(.32,.34,.03),steel)
 replacements['FIT_'+n+'_Basin']=[o.name for o in set(asset.objects)-before]
# Urinal faces west, with a projecting lower bowl and raised ceramic backsplash.
before=set(asset.objects)
o=bowl('Men_Urinal_shell',(13.57,15.83,.68),.235,.23,[(.12,-.15),(.65,-.145),(1,-.015),(.99,.018),(.85,.028),(.74,-.012),(.35,-.095),(.12,-.10)],cream)
tube('Men_Urinal_drain',[(13.57,15.83,.576),(13.57,15.83,.585)],.028,steel)
box('Men_Urinal_back',(13.765,15.83,.95),(.09,.45,.60),cream,.045)
tube('Men_Urinal_flush',[(13.73,15.83,1.23),(13.73,15.83,1.48),(13.80,15.83,1.48)],.016,steel)
box('Men_Urinal_flush_valve',(13.73,15.83,1.36),(.065,.07,.12),steel,.02)
tube('Men_Urinal_waste',[(13.60,15.83,.58),(13.60,15.83,.43),(13.79,15.83,.43)],.025,steel)
tube('Men_Urinal_supply_flange',[(13.825,15.83,1.48),(13.795,15.83,1.48)],.033,steel)
tube('Men_Urinal_waste_flange',[(13.825,15.83,.43),(13.785,15.83,.43)],.043,steel)
for dd in [15.68,15.98]:box('Men_Urinal_hanger',(13.805,dd,1.17),(.04,.06,.055),steel,.004)
replacements['FIT_Urinal']=[o.name for o in set(asset.objects)-before]
o=box('Men_Urinal_privacy',(13.515,15.35,.99),(.61,.035,1.48),petrol,.018);replacements['FIT_Urinal_privacy']=[o.name]
for xx in [13.26,13.75]:
 tube('Men_Privacy_foot',[(xx,15.35,.025),(xx,15.35,.29)],.022,steel)
 box('Men_Privacy_base',(xx,15.35,.025),(.11,.11,.035),steel)
bpy.context.view_layer.update()
# Centre each mesh data block without changing its installed geometry or parent hinge.
for o in asset.objects:
 if o.type=='MESH':
  center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  o.data.transform(Matrix.Translation(-center));o.matrix_basis=o.matrix_basis@Matrix.Translation(center)
bpy.context.view_layer.update()
# All generated asset geometry remains separate/editable, local object origins documented in inventory.
for o in asset.objects:
 o['package']='PLR';o['export_asset']=True
review.hide_render=True
s.frame_set(1);s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
for x,d in [(9,12.3),(12,12.3),(9.4,14.5),(12.4,14.5),(9.4,16.3),(12.4,16.3)]:
 ld=bpy.data.lights.new('PLR_TEMP_REVIEW_AREA','AREA');ld.energy=110;ld.shape='DISK';ld.size=1.5;ob=bpy.data.objects.new(ld.name,ld);review.objects.link(ob);ob.location=W((x,d,3.0));ob['temporary_review_light']=True
# Review lights are enabled while swing arcs remain optional.
review.hide_render=False
for o in review.objects:
 if o.type=='MESH':o.hide_render=True
(P/'replacement_manifest.json').write_text(json.dumps(dict(source_sha256=SHA,replacements=replacements,pivots=pivots,assembly_transform='W(x,depth,z)=(x-24.1,4-depth,z+4), metres; mesh objects use documented world matrices',patch=changes,export_collection='PLR_Assets',excluded=['PLR_REFERENCE_ONLY','PLR_REVIEW_ONLY']),indent=2))
(P/'previews').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'),compress=True)
print('PLR BUILD SAVED',len(asset.objects))
