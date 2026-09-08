"""Editable keyed-door study, with separate cylinder, plug, key and latch animation."""
import bpy, bmesh, math, ast, json, random
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
OUT.mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'door_study_03/Maldek_Digital_Door_Variants.blend'))
s=bpy.context.scene;s.frame_set(1)
for n in ast.parse((OUT.parent/'door_study_01/scripts/build_door.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['mat','link','box','cyl','rod','text','camera']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),'door_helpers','exec'))
stage=bpy.data.collections['90_Studio'];leaf=bpy.data.collections['01_Moving_leaf'];hinge=bpy.data.objects['D01_HINGE_PIVOT'];hinge.animation_data_clear()
for name in ['04_Digital_keypad','05_Interior_electronics','06_Electronic_strike']:
 bpy.data.collections[name].hide_render=True;bpy.data.collections[name].hide_viewport=True
for o in list(leaf.objects):
 if o.name.startswith(('Lock_cylinder','Key_slot')):bpy.data.objects.remove(o,do_unlink=True)
def col(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
housing=col('07_Key_cylinder_housings');plugcol=col('08_Rotating_plugs');keycol=col('09_Cut_service_key');guides=col('10_Animation_controls')
brass=mat('D04_Aged_brass',(.34,.22,.075),.82,.36);edge=mat('D04_Polished_brass',(.57,.39,.14),.85,.27)
dark=mat('D04_Keyway_shadow',(.011,.008,.004),.05,.85);patina=mat('D04_Recess_patina',(.072,.065,.035),.5,.65)
steel=bpy.data.materials['D01_Brushed_stainless'];rubber=bpy.data.materials['D01_EPDM']
for m in [brass,edge]:
 p=m.node_tree.nodes.get('Principled BSDF');noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=185
 bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.000035;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
def parent_keep(o,p):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
def empty(n,p):
 o=bpy.data.objects.new(n,None);guides.objects.link(o);o.location=p;o.empty_display_type='ARROWS';o.empty_display_size=.025;bpy.context.view_layer.update();return o
def difference(o,tool):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('True machined opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
 bpy.ops.object.modifier_move_up(modifier=mod.name)
 if len(o.modifiers)>2:bpy.ops.object.modifier_move_up(modifier=mod.name)
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def ring(n,p,outer,inner,depth,m,slot=False):
 # Explicit quad rings avoid Boolean cap n-gons around a small machined opening.
 vs=[];fs=[];N=64
 for y in [-depth/2,depth/2]:
  for inside in [False,True]:
   for i in range(N):
    a=2*math.pi*i/N;x,z=math.cos(a),math.sin(a)
    r=min(.0014/max(abs(x),1e-8),.0041/max(abs(z),1e-8)) if inside and slot else inner if inside else outer
    vs.append((p[0]+r*x,p[1]+y,p[2]+r*z))
 for i in range(N):
  j=(i+1)%N
  for a,b in [(0,N),(2*N,3*N),(0,2*N),(N,3*N)]:fs.append((a+i,a+j,b+j,b+i))
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(vs,[],fs);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 o=bpy.data.objects.new(n,mesh);group.objects.link(o);mesh.materials.append(m);mod=o.modifiers.new('Machined edge','BEVEL');mod.width=min(.00018,depth*.15);mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
group=housing
for o in [bpy.data.objects['Leaf_slab'],bpy.data.objects['Interior_enamel']]:
 tool=cyl('Cut_tool',(1.15,0,1),.0143,.12,dark,'Y',64);tool.modifiers.clear();difference(o,tool)
ring('Through_leaf_barrel',(1.15,0,1),.014,.0107,.064,brass)
plugs=[]
for side in [-1,1]:
 group=housing
 ring('Cylinder_seal_'+str(side),(1.15,side*.034,1),.0175,.014,.002,rubber)
 ring('Brass_security_collar_'+str(side),(1.15,side*.040,1),.0165,.0107,.011,brass)
 ring('Turned_face_rim_'+str(side),(1.15,side*.046,1),.016,.0148,.0015,edge)
 # True clearance between fixed collar and rotating core.
 ring('Recessed_plug_bearing_'+str(side),(1.15,side*.038,1),.01065,.0102,.004,patina)
 text('Cylinder_stamp_'+str(side),'M / 90',(1.15,side*.047,1.0116),.0024,patina,back=side>0)
 for x in [1.139,1.161]:
  o=box('Index_mark',(x,side*.047,1),(.0018,.0003,.00045),patina,.0001)
 group=plugcol
 pivot=empty('D04_PLUG_'+('FRONT' if side<0 else 'BACK'),(1.15,side*.046,1));parent_keep(pivot,hinge);plugs.append(pivot)
 plug=ring('Rotating_brass_core_'+str(side),(1.15,side*.040,1),.01015,0,.012,edge,slot=True)
 # 2.8 x 8.2 mm opening; dark backing is recessed 4 mm, never coplanar.
 parent_keep(plug,pivot)
 cavity=box('Keyway_recess_'+str(side),(1.15,side*.025,1),(.004,.001,.010),dark,0);parent_keep(cavity,pivot)
 lip=box('Keyway_ward_'+str(side),(1.1508,side*.040,.9986),(.00045,.010,.0005),patina,.0001);parent_keep(lip,pivot)
for o in housing.objects:parent_keep(o,hinge)
group=keycol
# Key points into +Y. Blade is vertical in the keyway and turns about Y.
keyroot=empty('D04_KEY_INSERT_AND_TURN',(1.15,-.046,1));parent_keep(keyroot,hinge)
# Profile is constructed in Y/Z, with five visible cut shoulders and a chamfered tip.
profile=[(-.012,-.0034),(.020,-.0034),(.024,-.0015),(.024,.0014),(.022,.0034),(.020,.0012),(.018,.0034),(.016,.0020),(.014,.0034),(.012,.0008),(.010,.0034),(.008,.0017),(.006,.0034),(.004,.0011),(.002,.0034),(-.012,.0034)]
verts=[(1.15+x,-.046+y,1+z) for x in [-.001,.001] for y,z in profile];n=len(profile);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('Five-cut blade profile');mesh.from_pydata(verts,[],faces);mesh.update();blade=bpy.data.objects.new('Five_cut_brass_blade',mesh);group.objects.link(blade);blade.data.materials.append(edge)
bevel=blade.modifiers.new('Deburred blade edges','BEVEL');bevel.width=.00016;bevel.segments=2;blade.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
# Longitudinal grooves are cut into both sides, stopping before the shoulder.
for side in [-1,1]:
 tool=box('Cut_tool',(1.15+side*.001,-.039,1-.0014),(.0006,.030,.0007),dark,0);difference(blade,tool)
# Soft pear-shaped bow: broad at the ring end, tapering naturally into the neck.
outline=[(-.074+.016*math.cos(2*math.pi*i/64),1+.015*(.82-.18*math.cos(2*math.pi*i/64))*math.sin(2*math.pi*i/64)) for i in range(64)]
vs=[(1.15+x,y,z) for x in [-.00125,.00125] for y,z in outline];fs=[tuple(range(63,-1,-1)),tuple(range(64,128))]+[(i,(i+1)%64,(i+1)%64+64,i+64) for i in range(64)]
me=bpy.data.meshes.new('Organic service-key bow');me.from_pydata(vs,[],fs);me.update();bow=bpy.data.objects.new('Pear_shaped_key_bow',me);group.objects.link(bow);me.materials.append(brass)
mod=bow.modifiers.new('Worn rolled edge','BEVEL');mod.width=.0007;mod.segments=4;bow.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
# Real ring hole through bow thickness, on key's X axis.
tool=cyl('Cut_tool',(1.15,-.083,1),.004,.012,dark,'X',48);tool.modifiers.clear();difference(bow,tool)
box('Shoulder_stop',(1.15,-.058,1),(.003,.004,.011),brass,.0007)
# Face engraving on the broad X-facing bow, with dark stamped characters.
label=text('Key_stamp','M-01',(1.15135,-.072,.994),.005,patina);label.rotation_euler=(math.pi/2,0,math.pi/2)
# Brass wear strokes stay on the bow face and below the lever's operating sweep.
random.seed(90)
for i in range(9):box('Key_use_scuff',(1.1513,random.uniform(-.078,-.063),random.uniform(.991,1.009)),(.00012,random.uniform(.001,.004),.00012),edge,.00003)
for o in list(keycol.objects):parent_keep(o,keyroot)
base=keyroot.location.copy()
for f,offset,turn in [(1,-.08,0),(12,-.08,0),(30,0,0),(48,0,90),(58,0,90),(70,0,0),(88,-.08,0),(104,-.08,0)]:
 keyroot.location=base+Vector((0,offset,0));keyroot.rotation_euler.y=math.radians(turn);keyroot.keyframe_insert(data_path='location',frame=f);keyroot.keyframe_insert(data_path='rotation_euler',frame=f)
for f,turn in [(1,0),(30,0),(48,90),(58,90),(70,0),(120,0)]:
 plugs[0].rotation_euler.y=math.radians(turn);plugs[0].keyframe_insert(data_path='rotation_euler',frame=f)
for f,angle in [(1,0),(88,0),(120,-95)]:hinge.rotation_euler.z=math.radians(angle);hinge.keyframe_insert(data_path='rotation_euler',frame=f)
latch=bpy.data.objects['Latch_tongue'];lb=latch.location.copy()
for f,dx in [(1,0),(46,0),(52,-.012),(88,-.012),(100,0),(120,0)]:latch.location=lb+Vector((dx,0,0));latch.keyframe_insert(data_path='location',frame=f)
s.frame_end=120;s.render.fps=24
for f,n in [(1,'KEY AVAILABLE'),(30,'INSERTED'),(48,'TURN 90 / RELEASE'),(70,'RETURN TO WITHDRAW'),(88,'KEY WITHDRAWN'),(120,'DOOR OPEN')]:s.timeline_markers.new(n,frame=f)
camera('10_Cylinder_and_key',(1.34,-.46,1.14),(1.15,-.08,1.015),68)
camera('11_Cylinder_macro',(1.23,-.235,1.06),(1.15,-.045,1.005),75)
camera('12_Key_profile',(1.40,-.20,1.09),(1.15,-.17,1.0),75)
s.cycles.samples=40;s.render.resolution_x=1400;s.render.resolution_y=1000;s.camera=bpy.data.objects['10_Cylinder_and_key'];s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Keyed_Door.blend'))
for name,cam,frame in [('01_Key_ready','10_Cylinder_and_key',1),('02_Inserted','11_Cylinder_macro',30),('03_Turned','11_Cylinder_macro',48),('04_Key_profile','12_Key_profile',1),('05_Door_open','02_Open',120)]:
 s.frame_set(frame);s.camera=bpy.data.objects[cam];s.render.filepath=str(OUT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(1);s.camera=bpy.data.objects['10_Cylinder_and_key'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Keyed_Door.blend'))
(OUT/'design_manifest.json').write_text(json.dumps({'scope':'Blender keyed-door design and animation; game integration pending','cylinder_diameter_mm':33,'plug_diameter_mm':20.3,'key_blade_thickness_mm':2,'keyway_mm':[2.8,8.2],'turn_degrees':90,'key_available_initially':True,'later_inventory_requirement':'Separate key possession from the lock animation; grant the matching key by default initially.','frames':{'ready':1,'inserted':30,'turned':48,'returned':70,'withdrawn':88,'open':120},'source':'door_study_03/Maldek_Digital_Door_Variants.blend','surface_ownership':'Old cylinder and painted key-slot objects removed; new collar, rotating plug and recessed cavity own the visible surfaces.'},indent=2))
