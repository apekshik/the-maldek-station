"""Blender-only review: stationary neon departure indicator beside approved cabin."""
import bpy, math, json, random, runpy
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parents[1]
REPO=OUT.parents[2]
(OUT/'previews').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(REPO/'art/blender/gondola_cabin_01/Maldek_Gondola_Cabin.blend'))
s=bpy.context.scene
s.frame_set(180)
# Freeze the reference cabin in boarding pose. This file is a separate design study.
for o in s.objects:
 if o.animation_data:o.animation_data_clear()
s.sequence_editor_clear()
s.timeline_markers.clear()
group=bpy.data.collections.new('NS01_Stationary_sign');s.collection.children.link(group)
root=bpy.data.objects.new('NS01_Mount_origin',None);group.objects.link(root)
root.location=(2.55,-3.35,0)
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 group.objects.link(o);o.parent=root;return o
def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new('NS01_'+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
enamel=mat('Petrol_enamel',(.035,.075,.064),.45,.4)
brass=mat('Aged_brass',(.35,.24,.095),.75,.38)
dark=mat('Recess_black',(.012,.020,.018),.15,.48)
ceramic=mat('Porcelain',(.42,.38,.28),.05,.35)
ink=mat('Warm_lettering',(.67,.57,.35),.1,.5)
steel=mat('Galvanized_steel',(.24,.27,.25),.8,.36)
rubber=mat('Cable_rubber',(.012,.014,.013),0,.8)
concrete=mat('Platform_concrete',(.14,.15,.13),0,.88)
def box(name,p,d,m,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=link(bpy.context.object);o.name='NS01_'+name;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:mod=o.modifiers.new('Fabrication edge radius','BEVEL');mod.width=bevel;mod.segments=3
 return o
def cyl(name,p,r,depth,m,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=p);o=link(bpy.context.object);o.name='NS01_'+name
 if axis=='Y':o.rotation_euler.x=math.pi/2
 o.data.materials.append(m);mod=o.modifiers.new('Edge','BEVEL');mod.width=.001;mod.segments=2;return o
def tube(name,pts,r,m):
 c=bpy.data.curves.new('NS01_'+name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new('NS01_'+name,c);group.objects.link(o);o.parent=root;c.materials.append(m);return o
def label(name,body,p,size,m):
 c=bpy.data.curves.new('NS01_'+name,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.00035
 o=bpy.data.objects.new('NS01_'+name,c);group.objects.link(o);o.parent=root;o.location=p;o.rotation_euler.x=math.pi/2;c.materials.append(m);return o

# Cabinet: open front, recessed face, separate side walls. No doubled front planes.
box('Cabinet_back',(0,.09,2.18),(1.48,.04,1.39),enamel)
box('Recessed_face',(0,.056,2.18),(1.414,.026,1.324),dark)
for x in [-.724,.724]:box('Cabinet_side',(x,0,2.18),(.032,.18,1.39),enamel)
for z in [1.501,2.859]:box('Cabinet_end',(0,0,z),(1.416,.18,.032),enamel)
for x in [-.707,.707]:box('Outer_brass_border',(x,-.097,2.18),(.016,.012,1.35),brass)
for z in [1.513,2.847]:box('Outer_brass_border',(0,-.097,z),(1.398,.012,.016),brass)
for x in [-.669,.669]:box('Inner_pinstripe',(x,-.095,2.18),(.004,.006,1.27),ink,.0005)
for z in [1.547,2.813]:box('Inner_pinstripe',(0,-.095,z),(1.342,.006,.004),ink,.0005)
box('Rain_hood',(0,-.018,2.894),(1.55,.285,.027),enamel,.004)
box('Rain_drip',(0,-.15,2.872),(1.55,.020,.055),enamel)
label('Header','M A L D E K   /   G O N D O L A',(0,-.061,2.744),.043,ink)
label('Footer','PLATFORM 01     •     MOUNTAIN SERVICE',(0,-.061,1.609),.031,ink)
for z in [2.66,2.415,2.185,1.940,1.678]:box('Row_rule',(0,-.040,z),(1.26,.003,.003),brass,.0004)
for x in [-.696,.696]:
 for z in [1.568,2.790]:
  cyl('Face_screw',(x,-.109,z),.010,.008,steel,'Y');box('Screw_slot',(x,-.114,z),(.012,.002,.002),dark,.0003)
# Steel post and properly attached cabinet brackets, foot flange and anchor hardware.
box('Post',(0,.155,.765),(.09,.09,1.53),enamel,.006)
box('Foot_flange',(0,.155,.021),(.32,.26,.032),steel)
for x in [-.115,.115]:
 for y in [.07,.24]:cyl('Anchor_bolt',(x,y,.047),.013,.022,brass)
for z in [1.61,2.66]:box('Rear_mount_rail',(0,.159,z),(.80,.105,.066),steel)
box('Rear_spine',(0,.16,2.10),(.09,.09,1.20),enamel)
box('Transformer_box',(0,.24,1.92),(.41,.15,.36),enamel,.009)
label('Transformer_plate','NS-01 / 1991',(0,.323,1.92),.025,ink).rotation_euler=(math.pi/2,0,math.pi)
for x in [-.165,.165]:
 for z in [1.785,2.055]:cyl('Rear_cover_screw',(x,.32,z),.007,.008,steel,'Y')
for x in [-.72,.72]:
 for z in [1.84,2.49]:box('Case_hinge',(x,.07,z),(.03,.035,.10),brass)
tube('Supply_conduit',[(0,.29,1.78),(0,.29,1.38),(.065,.29,1.3),(.065,.24,.09)],.012,rubber)
for z in [.28,.9,1.36]:box('Conduit_saddle',(.065,.25,z),(.039,.022,.026),steel)

# Monoline glass lettering, authored as actual 10 mm tubes and separate circuits.
# Curved bowls use sampled ellipses; every path has supported porcelain electrodes.
def arc(cx,cy,rx,ry,a,b,n=16):return [(cx+rx*math.cos(t),cy+ry*math.sin(t)) for t in [a+(b-a)*i/n for i in range(n+1)]]
font={
 'A':[[(0,0),(.30,1),(.60,0)],[(.12,.40),(.48,.40)]],
 'B':[[(0,0),(0,1)],[(0,1),(.30,1)]+arc(.30,.75,.28,.25,math.pi/2,-math.pi/2)+[(0,.50)],[(0,.50),(.30,.50)]+arc(.30,.25,.30,.25,math.pi/2,-math.pi/2)+[(0,0)]],
 'D':[[(0,0),(0,1),(.20,1)]+arc(.20,.5,.40,.5,math.pi/2,-math.pi/2)+[(0,0)]],
 'E':[[(.60,1),(0,1),(0,0),(.60,0)],[(0,.50),(.48,.50)]],
 'G':[arc(.30,.50,.30,.50,.25*math.pi,1.94*math.pi)+[(.60,.44),(.34,.44)]],
 'I':[[(.30,0),(.30,1)]],
 'N':[[(0,0),(0,1),(.60,0),(.60,1)]],
 'O':[arc(.30,.50,.30,.50,0,2*math.pi,32)],
 'P':[[(0,0),(0,1),(.30,1)]+arc(.30,.75,.30,.25,math.pi/2,-math.pi/2)+[(0,.5)]],
 'R':[[(0,0),(0,1),(.30,1)]+arc(.30,.75,.30,.25,math.pi/2,-math.pi/2)+[(0,.5)],[(.30,.5),(.63,0)]],
 'T':[[(0,1),(.60,1)],[(.30,1),(.30,0)]],
 'V':[[(0,1),(.30,0),(.60,1)]],
 'W':[[(0,1),(.10,0),(.30,.65),(.50,0),(.60,1)]],
 'Y':[[(0,1),(.30,.53),(.60,1)],[(.30,.53),(.30,0)]]}
states=[('BOARD',2.47,(.28,1,.55),1),('ARRIVING',2.23,(1,.52,.12),49),('DEPART',1.99,(1,.24,.06),97),('AWAY',1.75,(.38,.65,1),145)]
materials=[]
for word,z,color,frame in states:
 m=mat('Circuit_'+word,tuple(v*.19 for v in color),.15,.25);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*color,1);materials.append(m)
 height=.135 if len(word)>6 else .155;advance=height*.90;width=((len(word)-1)*.90+.60)*height
 for i,ch in enumerate(word):
  x=-width/2+i*advance
  for j,path in enumerate(font[ch]):
   pts=[(x+u*height,-.036,z+v*height) for u,v in path];tube('Neon_'+word+'_'+str(i)+'_'+str(j),pts,.005,m)
   for u,v in [path[0],path[-1]]:
    cyl('Electrode_'+word,(x+u*height,-.004,z+v*height),.009,.048,ceramic,'Y')
 # Circuit indicator at left; all labels use the same physical colour per circuit.
 tube('Pilot_'+word,[(-.57+.013*math.cos(t),-.038,z+.075+.013*math.sin(t)) for t in [i*2*math.pi/24 for i in range(25)]],.003,m)
 label('Index_'+word,str(len(materials)).zfill(2),(.584,-.049,z+.075),.032,ink)
 for _,_,_,f in states:
  p.inputs['Emission Strength'].default_value=7 if frame==f else .015;p.inputs['Emission Strength'].keyframe_insert('default_value',frame=f)
 for fc in m.node_tree.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 s.timeline_markers.new(word,frame=frame)

# Provisional platform footprint only; no station architecture is changed.
context=bpy.data.collections.new('NS01_Review_platform_only');s.collection.children.link(context)
o=box('Review_platform',(0,-.15,-.13),(5.7,3.0,.25),concrete,.012)
group.objects.unlink(o);context.objects.link(o);o.parent=None;o.location=(.65,-3.85,-.13)
s.frame_start=1;s.frame_end=192;s.render.fps=24
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=1100;s.render.resolution_percentage=100
def camera(name,pos,target,lens):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;d.lens=lens;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
close=camera('NS01_Close_review',(4.45,-7.7,3.35),(2.55,-3.35,2.20),68)
contextcam=camera('NS01_Placement_review',(7.9,-12.8,4.9),(.8,-1.5,1.8),48)
rear=camera('NS01_Rear_detail',(4.6,-.4,2.95),(2.55,-3.2,1.91),65)
# Local fill preserves cabinet detail without bleaching the glow.
d=bpy.data.lights.new('NS01_Review_softbox','AREA');d.energy=65;d.shape='DISK';d.size=2;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(4,-5,4);o.rotation_euler=(Vector((2.55,-3.35,2.2))-o.location).to_track_quat('-Z','Y').to_euler()
tree=bpy.data.node_groups.new('NS01_Neon_glow','CompositorNodeTree');s.compositing_node_group=tree;tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');nodes=tree.nodes;rl=nodes.new('CompositorNodeRLayers');gl=nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Quality'].default_value='High';gl.inputs['Strength'].default_value=.5;out=nodes.new('NodeGroupOutput');tree.links.new(rl.outputs['Image'],gl.inputs['Image']);tree.links.new(gl.outputs['Image'],out.inputs['Image'])
runpy.run_path(str(OUT/'scripts/finish.py'),run_name='sign_finish')['finish']()
s.frame_set(1);s.camera=close
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Gondola_Status_Sign.blend'))
for name,cam,frame in [('01_BOARD',close,1),('02_ARRIVING',close,49),('03_DEPART',close,97),('04_AWAY',close,145),('05_Placement',contextcam,1),('06_Rear',rear,1)]:
 s.camera=cam;s.frame_set(frame);s.render.filepath=str(OUT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=close;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Gondola_Status_Sign.blend'))
(OUT/'design_manifest.json').write_text(json.dumps({'scope':'Blender design awaiting user approval; no game installation','cabinet_dimensions_m':[1.48,.20,1.39],'overall_height_m':2.908,'root_relative_to_cabin_floor_m':[2.55,-3.35,0],'cabinet_inner_x_m':1.775,'cabin_handle_outer_x_m':1.43,'lateral_separation_m':.345,'states':{w:f for w,z,c,f in states},'tube_diameter_m':.010,'future_mapping':{'BOARD':'Docked, landing ready and doors fully open','ARRIVING':'Cabin approaching or settling; boarding unavailable','DEPART':'Departure requested, closing and latch sequence','AWAY':'Cabin absent; boarding unavailable'},'review_context':'Approved cabin frozen open; provisional platform slab, not final station placement'},indent=2))
