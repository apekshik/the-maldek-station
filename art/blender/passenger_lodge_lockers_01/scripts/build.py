"""Build isolated PLL bank; source is opened read-only and never overwritten."""
import bpy, math, json, hashlib, os, re
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
SRC=Path(os.environ.get('MALDEK_ASSET_REPO','C:/Users/apek-anna/Developer/the-maldek-station'))/'art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
EXPECTED='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
for other in list(bpy.data.scenes):
 if other!=s:bpy.data.scenes.remove(other)
s.name='PLL_Fitted_Review'
# Preserve source layer exclusions when wrapping context in a reference collection.
for lc in bpy.context.view_layer.layer_collection.children:
 if lc.exclude:lc.collection.hide_render=True;lc.collection.hide_viewport=True
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
replace=[]
for o in list(s.objects):
 if re.match(r'^FIT_Locker_\d{2}(?:_Door|_Number)?$',o.name) or o.name.startswith(('PL03_Locker_Handle','PL03_Locker_Vent')):
  replace.append({'name':o.name,'bounds':bounds(o),'collections':[c.name for c in o.users_collection]});bpy.data.objects.remove(o,do_unlink=True)
assert len(replace)==96,len(replace)
ref=bpy.data.collections.new('REFERENCE_ONLY_Source_Context');s.collection.children.link(ref);ref['export']=False
for c in list(s.collection.children):
 if c!=ref:s.collection.children.unlink(c);ref.children.link(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o);ref.objects.link(o)
bpy.data.collections['PL03_Removable_Roof'].hide_render=True;bpy.data.collections['PL03_Removable_Roof'].hide_viewport=True
col=bpy.data.collections.new('PLL_Lockers');s.collection.children.link(col)
review=bpy.data.collections.new('REVIEW_ONLY_Cameras_Lights');s.collection.children.link(review);review['export']=False
paint=bpy.data.materials['VF06_Petrol_paint'];zinc=bpy.data.materials['VF06_Galvanized'];enamel=bpy.data.materials['VF06_Warm_enamel'];dark=bpy.data.materials['VF06_Structural_steel']
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
brass=mat('PLL_Satin_Nickel_Brass',(.38,.31,.17),.8);ink=mat('PLL_Number_Ink',(.025,.033,.031));inside=mat('PLL_Interior_Light_Galvanized',(.39,.43,.40),.65,.5)
cache={}
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
def box(name,p,d,m,parent=None,bevel=.0005):
 key=(tuple(d),m.name,bevel)
 if key in cache:o=bpy.data.objects.new(name,cache[key]);col.objects.link(o)
 else:
  bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;link(o);o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
  if bevel:
   mod=o.modifiers.new('Fold edge radius','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  cache[key]=o.data
 o.name=name;o.parent=parent;o.location=p;return o
def cyl(name,p,r,h,m,parent=None,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=h);o=bpy.context.object;o.name=name;link(o);o.data.materials.append(m);o.parent=parent;o.location=p
 if axis=='Y':o.rotation_euler.x=math.pi/2
 return o
def empty(name,p,parent=None):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.location=p;o.empty_display_size=.07;return o
s.collection.children.unlink(ref) # Suspend heavy context dependency updates during authoring.
roots=[];doors=[]
for i in range(12):
 tag=f'PLL_{i+1:02}';root=empty(tag+'_Assembly',(-14.1+i*.32,-7,4));roots.append(root);root['locker_id']=f'{i+1:02}';print('Building',tag,flush=True)
 def B(n,p,d,m=paint,parent=root,bevel=.0005):return box(tag+'_'+n,p,d,m,parent,bevel)
 # Folded carcass, floor and plinth: exclusive panel spans, no duplicate shells.
 B('Side_L',(.00075,.25,.9485),(.0015,.5,1.797));B('Side_R',(.29925,.25,.9485),(.0015,.5,1.797))
 B('Back',(.15,.00075,.9485),(.296,.0015,1.797),inside)
 B('Bottom',(.15,.246,.081),(.296,.489,.002),inside)
 B('Top_Cap',(.15,.25,1.8485),(.3,.5,.003))
 B('Plinth_Front',(.15,.47,.025),(.296,.003,.05),dark);B('Plinth_Rear',(.15,.025,.025),(.296,.003,.05),dark)
 for x in [.026,.274]:B('Plinth_Foot', (x,.25,.025),(.035,.43,.05),dark)
 for x in [.007,.293]:
  B('Frame_Lip', (x,.4985,.954),(.014,.003,1.788));B('Frame_Return',(x,.485,.954),(.002,.024,1.788),inside)
 B('Frame_Sill',(.15,.4985,.068),(.272,.003,.024))
 B('Frame_Header',(.15,.4985,1.8135),(.272,.003,.067))
 B('Shelf',(.15,.239,1.382),(.27,.455,.002),inside)
 B('Shelf_Fold',(.15,.466,1.371),(.27,.002,.019),inside)
 for x in [.015,.285]:B('Shelf_Support',(x,.23,1.373),(.018,.41,.003),zinc)
 # Rear attachment straps bridge the approved 200mm wall stand-off; no master patch.
 for z in [.23,1.70]:
  B('Wall_Brace',(.15,-.097,z),(.05,.197,.003),zinc)
  B('Wall_Tab',(.15,-.194,z+.022),(.05,.003,.041),zinc)
  cyl(tag+'_Wall_Anchor',(.15,-.199,z+.028),.005,.020,zinc,root,'Y')
 # Hook assembled from capped mesh cylinders, no curve cap defects.
 cyl(tag+'_Hook_Base',(.15,.008,1.57),.015,.008,zinc,root,'Y')
 cyl(tag+'_Hook_Arm',(.15,.037,1.57),.004,.05,zinc,root,'Y')
 cyl(tag+'_Hook_Tip',(.15,.06,1.582),.004,.025,zinc,root)
 door=empty(tag+'_Door_Pivot',(.014,.528,.086),root);doors.append(door);door['closed_degrees']=0;door['open_limit_degrees']=100;door['axis']='local +Z'
 # Real 1.5mm face with punched openings; no backing panel across vents.
 leaf=B('Door_Sheet',(.136,-.006, .844),(.268,.0015,1.688),paint,door)
 # Make unique before subtracting apertures.
 leaf.data=leaf.data.copy()
 for base in [.16,1.40]:
  for j in range(4):
   z=base+j*.028
   cut=B('TEMP_VentCut',(.13,-.006,z),(.176,.03,.010),dark,door,0)
   bpy.context.view_layer.update();bpy.context.view_layer.objects.active=leaf
   mod=leaf.modifiers.new('Punched vent','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
   blade=B('Louvre',(.13,.0008,z+.005),(.18,.0015,.016),paint,door);blade.rotation_euler.x=math.radians(-35)
 for x in [.003,.269]:B('Door_Fold_Side',(x,-.014,.844),(.0015,.014,1.684),paint,door)
 for z in [.001,1.687]:B('Door_Fold_End',(.136,-.014,z),(.264,.014,.0015),paint,door)
 for z in [.24,1.43]:
  cyl(tag+'_Hinge_Pin', (0,0,z),.003,.067,zinc,door)
  # Sleeves split below; no coincident sleeve shells.
  # Fixed and rotating sleeves share a real common axis, with axial separation.
  for dz in [-.024,.024]:cyl(tag+'_Hinge_FixedSleeve',(.014,.528,.086+z+dz),.006,.019,zinc,root)
  cyl(tag+'_Hinge_MovingSleeve',(0,0,z),.006,.024,zinc,door)
  B('Hinge_Leaf',( .008,.513,.086+z),(.016,.002,.066),zinc,root)
  B('Hinge_DoorLeaf',(.015,-.003,z),(.025,.002,.025),zinc,door)
 # Modest pull, key cylinder and independent cam for later logic.
 for z in [.755,.84]:cyl(tag+'_Pull_Post',(.224,.009,z),.004,.027,zinc,door,'Y')
 cyl(tag+'_Pull_Grip',(.224,.023,.7975),.0045,.093,zinc,door)
 cyl(tag+'_Lock_Bezel',(.224,-.001,.904),.011,.007,zinc,door,'Y')
 cyl(tag+'_Lock_Plug',(.224,.003,.904),.0075,.002,brass,door,'Y')
 B('Keyway',(.224,.0042,.904),(.0018,.0005,.008),ink,door,.0001)
 cyl(tag+'_Lock_Barrel',(.224,-.021,.904),.008,.027,brass,door,'Y')
 cam=empty(tag+'_Lock_Cam_Pivot',(.224,-.036,.904),door)
 B('Lock_Cam',(.023,0,0),(.054,.003,.012),zinc,cam)
 cam.rotation_euler.y=0;cam.keyframe_insert('rotation_euler',frame=1)
 cam.rotation_euler.y=math.pi/2;cam.keyframe_insert('rotation_euler',frame=8)
 B('Strike',(.287,.476,.99),(.014,.003,.041),zinc,root)
 B('Number_Plate',(.135,-.003,1.28),(.087,.003,.046),enamel,door)
 for x in [.098,.172]:cyl(tag+'_Plate_Rivet',(x,-.0005,1.28),.002,.002,zinc,door,'Y')
 text=bpy.data.curves.new(tag+'_NumberText','FONT');text.body=f'{i+1:02}';text.align_x='CENTER';text.align_y='CENTER';text.size=.033;text.extrude=.00015
 o=bpy.data.objects.new(tag+'_Number',text);col.objects.link(o);o.parent=door;o.location=(.135,-.0009,1.28);o.rotation_euler=(math.pi/2,0,math.pi);o.data.materials.append(ink)
 # Three neighboring leaves open together in the saved timeline, closed at frame 1.
 door.rotation_euler.z=0;door.keyframe_insert('rotation_euler',frame=1);door.keyframe_insert('rotation_euler',frame=10)
 door.rotation_euler.z=math.radians(100 if i in [3,4,5] else 0);door.keyframe_insert('rotation_euler',frame=50)
 door.rotation_euler.z=math.radians(100);door.keyframe_insert('rotation_euler',frame=100)
s.collection.children.link(ref)
s.frame_end=100;s.frame_set(1)
# Reuse matching evaluated mesh data, including punched door variants, while keeping distinct objects.
leaf0=bpy.data.objects['PLL_01_Door_Sheet']
for i in range(2,13):bpy.data.objects[f'PLL_{i:02}_Door_Sheet'].data=leaf0.data
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.world.color=(.18,.18,.18)
for n,pos,power,size,target in [('Key',(-12,-4.8,7),330,4,(-12,-6.5,5)),('Fill',(-15,-5.7,6),160,3,(-12,-6.7,5)),('Rim',(-10,-6,6.8),140,2,(-12,-6.8,5)),('Rear',(-12,-8.6,6.5),300,3,(-12,-7,5))]:
 d=bpy.data.lights.new('REVIEW_TEMP_'+n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
views=[('bank_closed',(-12.19,-3.2,5.5),(-12.19,-6.65,4.95),28,1),('approach_open',(-14.4,-4.55,5.65),(-12.25,-6.55,4.95),32,50),('hardware',(-11.97,-5.60,5.04),(-11.956,-6.48,4.965),50,1),('interior',(-12.67,-5.20,5.25),(-12.67,-6.82,4.95),20,50),('rear_attachment',(-12.19,-9.6,5.2),(-12.19,-7,4.96),22,1)]
for n,p,t,l,f in views:
 d=bpy.data.cameras.new('REVIEW_'+n);o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=l;d.clip_start=.025
s.camera=bpy.data.objects['REVIEW_bank_closed']
bpy.context.view_layer.update()
manifest={'source_sha256':EXPECTED,'source_file':str(SRC),'replaced':replace,'collection':'PLL_Lockers','reference_only':['REFERENCE_ONLY_Source_Context','REVIEW_ONLY_Cameras_Lights'],'wall_patch':None,'units':'metres Z up','layout_mapping':'(x-24.1,4-depth,z+4)','body_dimensions_m':[.30,.50,1.85],'bank_body_bounds':[[-14.1,-7,4],[-10.28,-6.5,5.85]],'assemblies':[{'root':r.name,'translation':list(r.location),'rotation':[0,0,0],'door_pivot_local':list(d.location),'door_pivot_world':list(d.matrix_world.translation),'open_degrees':100} for r,d in zip(roots,doors)],'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'local_location':list(o.location),'dimensions':list(o.dimensions),'material_slots':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []} for o in col.objects],'instance_strategy':'Shared mesh datablocks for equal panels and all punched door sheets; separate per-locker transforms, door parents, number curves, keyed plugs and cams. No linked master data.','poses':{'1':'closed','50':'04/05/06 open 100 degrees','100':'all open 100 degrees'},'views':[{'name':n,'position':p,'target':t,'lens':l,'frame':f} for n,p,t,l,f in views]}
(OUT/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
# Editable fitted file; separate collection-only library is the delivery/export boundary.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'),compress=True)
bpy.data.libraries.write(str(OUT/'PLL_Asset_Only.blend'),{col},fake_user=True,compress=True)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==EXPECTED
print('PLL BUILD COMPLETE',len(col.objects))
