"""Source-fitted keyed lodge doors. Writes only this package; no runtime logic."""
import bpy, bmesh, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1]
SOURCE=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
EXPECTED='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED, 'Inspect changed source before rebuilding'
(OUT/'previews').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source_scene=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=source_scene
bpy.context.view_layer.update()
refs=[o for o in source_scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
s=bpy.data.scenes.new('PLD_Fitted_Doors');bpy.context.window.scene=s
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
def col(n,parent=None):
 c=bpy.data.collections.new(n);(parent or s.collection).children.link(c);return c
ref=col('PLD_REFERENCE_ONLY_Approved_Lodge');ref['export']=False
roof=col('PLD_REFERENCE_ONLY_Removable_Roof');roof['export']=False
ref_record=[]
reference_world={o:o.matrix_world.copy() for o in refs}
for o in refs:
 o.parent=None;o.matrix_world=reference_world[o]
 (roof if o.name.startswith('PL03_Roof') else ref).objects.link(o)
 ref_record.append(dict(name=o.name,matrix_world=[list(r) for r in o.matrix_world]))
roof.hide_render=True;roof.hide_viewport=True
for sc in list(bpy.data.scenes):
 if sc!=s:bpy.data.scenes.remove(sc)
for o in list(bpy.data.objects):
 if o.name not in s.objects:bpy.data.objects.remove(o,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
assets=col('PLD_ASSETS');assets['export']=True
review=col('PLD_REVIEW_ONLY');review['export']=False
patchcol=col('PLD_OPENING_PATCHES');patchcol['export']='replacement wall fragments only'
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
blue=bpy.data.materials['VF06_Petrol_paint'];cream=bpy.data.materials['VF06_Warm_enamel'];steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized']
ss=mat('PLD_Brushed_Stainless',(.43,.47,.46),.85,.32);brass=mat('PLD_Worn_Brass',(.39,.26,.09),.82,.34);rubber=mat('PLD_EPDM',(.009,.014,.013),0,.82)
glass=mat('PLD_Etched_Transmissive_Glass',(.79,.86,.83),0,.32)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
n=glass.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=420
t=glass.node_tree.nodes.new('ShaderNodeTexCoord');glass.node_tree.links.new(t.outputs['Object'],n.inputs['Vector'])
b=glass.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.0003;glass.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);glass.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
group=assets;prefix='PLD_';root=None;moving=None
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(prefix+n);me.from_pydata(v,[],f);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(prefix+n,me);group.objects.link(o)
 if m:me.materials.append(m)
 return o
def bevel(o,w=.001):
 if w:
  mod=o.modifiers.new('Manufactured_radius','BEVEL');mod.width=w;mod.segments=3
  o.modifiers.new('Weighted_normals','WEIGHTED_NORMAL')
 return o
def box(n,p,d,m,w=.001):
 x,y,z=p;a,b,c=[i/2 for i in d]
 v=[(x+dx*a,y+dy*b,z+dz*c) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return bevel(mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m),w)
def cyl(n,p,r,h,m,axis='Z',N=32):
 v=[]
 for a in [-h/2,h/2]:
  for i in range(N):
   ang=2*math.pi*i/N;u=r*math.cos(ang);w=r*math.sin(ang)
   q=(u,w,a) if axis=='Z' else (u,a,w) if axis=='Y' else (a,u,w)
   v.append(tuple(p[k]+q[k] for k in range(3)))
 return bevel(mesh(n,v,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m),.0004)
def ring(n,p,r,ri,h,m,slot=False):
 N=48;v=[];f=[]
 for y in [-h/2,h/2]:
  for inside in [False,True]:
   for i in range(N):
    a=2*math.pi*i/N;x,z=math.cos(a),math.sin(a)
    q=min(.0014/max(abs(x),1e-8),.0041/max(abs(z),1e-8)) if inside and slot else ri if inside else r
    v.append((p[0]+q*x,p[1]+y,p[2]+q*z))
 for i in range(N):
  j=(i+1)%N
  for a,b in [(0,N),(2*N,3*N),(0,2*N),(N,3*N)]:f.append((a+i,a+j,b+j,b+i))
 return bevel(mesh(n,v,f,m),.00012)
def return_lever(n,cx,cy,z,face):
 # One continuous bent tube, closed caps; no overlapping capped cylinders at elbows.
 path=[(cx,cy+face*.030,z),(cx,cy+face*.051,z)]
 for i in range(1,9):
  a=math.pi/2*i/8;path.append((cx-.020+.020*math.cos(a),cy+face*(.051+.020*math.sin(a)),z))
 path.append((cx-.100,cy+face*.071,z))
 for i in range(1,9):
  a=math.pi/2*i/8;path.append((cx-.100-.020*math.sin(a),cy+face*(.051+.020*math.cos(a)),z))
 path.append((cx-.120,cy+face*.044,z));v=[];f=[];N=20
 for i,point in enumerate(path):
  tangent=Vector(path[min(i+1,len(path)-1)])-Vector(path[max(0,i-1)]);tangent.normalize();cross=tangent.cross(Vector((0,0,1)))
  for j in range(N):
   a=2*math.pi*j/N;v.append(Vector(point)+.0095*(math.cos(a)*cross+math.sin(a)*Vector((0,0,1))))
 for i in range(len(path)-1):
  for j in range(N):f.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
 f.extend([tuple(reversed(range(N))),tuple(range((len(path)-1)*N,len(path)*N))])
 o=mesh(n,v,f,ss)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def diff(o,tool):
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Opening_cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name)
def empty(n,p):
 o=bpy.data.objects.new(prefix+n,None);group.objects.link(o);o.location=p;o.empty_display_type='ARROWS';o.empty_display_size=.09;return o
def parent(o,p):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=p;o.matrix_world=w
def text(n,body,p,size,face,m):
 cu=bpy.data.curves.new(prefix+n,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.0001
 o=bpy.data.objects.new(prefix+n,cu);group.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,math.pi if face>0 else 0);cu.materials.append(m);return o
def screw(n,p,face):
 o=cyl(n,p,.004,.002,ss,'Y',16)
 box(n+'_Slot',(p[0],p[1]+face*.00115,p[2]),(.005,.0003,.0008),rubber,.0001)
 return o
DOORS=[
 dict(id='ARRIVAL',width=1.2,height=2.3,origin=[-16.5,-7.232,4],yaw=180,side=1,wall='Hall_south_entry',parts=['0_0','1_2.3','2_0'],proxy='FIT_Court_door_sweep',label='LODGE',sub='ARRIVAL / 01',exterior=1,
 rationale='East jamb, outward into court: inward alternative clipped the coffee queue by 217 mm at intermediate swing. Outward leaf parks beside the east court wall; the approach through the moving doorway is occupied until fully open, while the coffee queue and remote court/staff routes stay clear.'),
 dict(id='GONDOLA',width=1.2,height=2.3,origin=[-16.5,3.82,4],yaw=180,side=1,wall='North',parts=['2_0','3_2.3','4_0'],proxy='FIT_North_door_sweep',label='PLATFORM',sub='GONDOLA / 02',exterior=-1,
 rationale='East jamb, inward into hall: no moving hardware enters the grating promenade at station Y=5.5; the east-side pocket lies clear of table and bench footprints.'),
 dict(id='STAFF',width=1.0,height=2.2,origin=[-19.068,-11,4],yaw=90,side=-1,wall='Coffee_east',parts=['0_0','1_2.2','2_0'],proxy='FIT_Staff_door_sweep',label='STAFF',sub='COFFEE / 03',exterior=-1,
 rationale='Depth-15 jamb, outward into court: preserves the rear prep run and kitchen work space; parks south of the staff crossing and west of the main arrival route. Staff aperture is fixed at local X=4.82, depth 14–15.')]
patches=[];manifest=[]
for spec in DOORS:
 prefix='PLD_'+spec['id']+'_';W=spec['width'];H=spec['height'];side=spec['side'];ext=spec['exterior']
 # Asset coordinates: u from hinge-side clear jamb to latch, +v completes RH basis.
 # The side parameter mirrors ALL hinge/stop/seal positions, not only animation.
 group=col(prefix+'Assembly',assets);assembly_group=group
 T=Matrix.Translation(Vector(spec['origin']))@Matrix.Rotation(math.radians(spec['yaw']),4,'Z')
 wall_depth=.212
 # Recess the rough aperture only where a jamb/header occupies the original core.
 for part in spec['parts']:
  for lead in ['FIT_','PL03_Cladding_FIT_']:
   name=lead+spec['wall']+'_'+part;o=bpy.data.objects[name]
   o.data=o.data.copy();before=len(o.data.vertices)
   tool=box('TEMP_PATCH_TOOL',(W/2,-side*wall_depth/2,H/2+.032),(W+.128,.65,H+.064),None,0);tool.matrix_world=T
   # Mesh coordinates already contain the local cutter centre.
   diff(o,tool);bpy.data.objects.remove(tool,do_unlink=True)
   for c in list(o.users_collection):c.objects.unlink(o)
   patchcol.objects.link(o);original=name;o.name=prefix+'PATCH_'+name
   o['replaces_source_object']=original;o['scope']='door-local rough aperture; no other openings changed'
   patches.append(dict(door=spec['id'],source_object=original,replacement_object=o.name,operation='DIFFERENCE',local_box_center=[W/2,-side*wall_depth/2,H/2+.032],local_box_dimensions=[W+.128,.65,H+.064],matrix_world=[list(r) for r in T],clear_aperture_m=[W,H],concealed_core_gap_m=.004))
 # Continuous 45 mm leaf, with physical window and cylinder apertures.
 center=side*.0525
 slab=box('Leaf_Steel',(W/2,center,(.018+H+.02)/2),(W+.03,.045,H+.002),blue,0)
 # Skin replaces outer 1 mm of slab, avoiding duplicate visible surfaces.
 slab.data.materials.append(cream)
 for f in slab.data.polygons:
  if f.normal.y*ext<-.5:f.material_index=1
 vl,vr,vb,vt=.13,W-.13,1.34,H-.14
 cut=box('TEMP_GLASS_CUT',(W/2,center,(vb+vt)/2),(vr-vl,.25,vt-vb),None,0);diff(slab,cut);bpy.data.objects.remove(cut,do_unlink=True)
 cx=W-.12
 cut=cyl('TEMP_CYLINDER_CUT',(cx,center,1.0),.0143,.25,None,'Y',64);cut.modifiers.clear();diff(slab,cut);bpy.data.objects.remove(cut,do_unlink=True);bevel(slab,.0006)
 box('Glass',(W/2,center,(vb+vt)/2),(vr-vl+.014,.008,vt-vb+.014),glass,.0004)
 # Glazing enters a rebated pocket; widen only the centre of the leaf's cutout.
 cut=box('TEMP_GLASS_REBATE',(W/2,center,(vb+vt)/2),(vr-vl+.022,.016,vt-vb+.022),None,0)
 slab.modifiers.clear();diff(slab,cut);bpy.data.objects.remove(cut,do_unlink=True);bevel(slab,.0006)
 for face in [-1,1]:
  for x in [vl,vr]:
   box('Glazing_Bead',(x,center+face*.027,(vb+vt)/2),(.022,.012,vt-vb+.022),steel)
   box('Glazing_Seal',(x,center+face*.009,(vb+vt)/2),(.01,.009,vt-vb-.002),rubber,.0007)
  for z in [vb,vt]:
   box('Glazing_Bead',(W/2,center+face*.027,z),(vr-vl-.022,.012,.022),steel)
   box('Glazing_Seal',(W/2,center+face*.009,z),(vr-vl-.01,.009,.01),rubber,.0007)
  y=center+face*.025
  box('Kick_Plate',(W/2,y,.22),(W-.10,.003,.31),ss,.001)
  for x in [.07,W/2,W-.07]:
   for z in [.085,.355]:screw('Kick_Fastener',(x,y+face*.0025,z),face)
  # 54 mm rosette, 19 mm grip, 135 mm lever reach; same hardware on every leaf.
  rosette=ring('Lever_Rose',(cx,center+face*.028,1.1),.027,.0042,.010,ss)
  handle=empty('HANDLE_'+('A' if face<0 else 'B'),(cx,center,1.1));handle['axis']='local Y';handle['rest_degrees']=0
  grip=return_lever('Return_Lever',cx,center,1.1,face);parent(grip,handle)
  ring('Cylinder_Collar',(cx,center+face*.03,1),.0165,.0107,.014,brass)
  ring('Cylinder_Gasket',(cx,center+face*.0235,1),.018,.0143,.002,rubber)
  plugroot=empty('KEY_PLUG_'+('A' if face<0 else 'B'),(cx,center+face*.034,1));plugroot['axis']='local Y';plugroot['keyway_mm']='2.8 x 8.2';plugroot['logic']='none'
  plug=ring('Rotating_Plug',(cx,center+face*.03,1),.01015,0,.012,brass,True);parent(plug,plugroot)
  backing=box('Recessed_Keyway',(cx,center+face*.020,1),(.004,.001,.010),rubber,0);parent(backing,plugroot)
  labely=center+face*.0255
  box('Enamel_ID_Plate',(W*.40,labely,1.17),(.38,.004,.15),cream,.002)
  text('Door_Label',spec['label'],(W*.40,labely+face*.0022,1.18),.043,face,steel)
  text('Door_Subtitle',spec['sub'],(W*.40,labely+face*.0022,1.13),.018,face,steel)
 ring('Through_Leaf_Cylinder',(cx,center,1),.014,.0107,.045,brass)
 # Hollow lock-edge plate and retractable latch, independent from the leaf control.
 box('Lock_Edge_Plate',(W+.016,center,1.06),(.002,.032,.22),ss,.0005)
 latch=box('LATCH',(W+.024,center,1.10),(.014,.019,.024),ss,.001)
 latch['axis']='local X';latch['retract_m']=.014;latch['logic']='none'
 # Door-bottom weather strip: retracting seal is review-only animation.
 bottom=box('BOTTOM_SEAL',(W/2,center,.014),(W+.012,.012,.008),rubber,.001)
 # Four public hinges / three staff, with independent alternating hollow knuckles.
 hinge_z=[.25,.88,1.51,H-.23] if W>1 else [.25,1.1,H-.23]
 fixed_parts=[]
 for z in hinge_z:
  box('Moving_Hinge_Strap',(-.006,side*.080,z),(.104,.009,.125),ss,.001)
  for dz in [-.05,0,.05]:
   # Cylindrical knuckles have actual pin bores; ring helper uses Y, rotate mesh into Z.
   kn=ring('Moving_Knuckle',(0,0,0),.0125,.0053,.024,ss)
   kn.data.transform(Matrix.Translation(Vector((-.06,side*.086,z+dz)))@Matrix.Rotation(math.pi/2,4,'X'))
  for dz in [-.04,.04]:screw('Hinge_Leaf_Screw',(.025,side*.086,z+dz),side)
  fixed_parts.append(box('Fixed_Hinge_Strap',(-.106,side*.080,z),(.070,.009,.125),ss,.001))
  for dz in [-.025,.025]:
   kn=ring('Fixed_Knuckle',(0,0,0),.0125,.0053,.024,ss);kn.data.transform(Matrix.Translation(Vector((-.06,side*.086,z+dz)))@Matrix.Rotation(math.pi/2,4,'X'));fixed_parts.append(kn)
  fixed_parts.append(cyl('Hinge_Pin',(-.06,side*.086,z),.005,.142,steel))
  for dz in [-.04,.04]:
   before=set(group.objects);screw('Hinge_Frame_Screw',(-.117,side*.086,z+dz),side);fixed_parts.extend(set(group.objects)-before)
 # All moving roots are captured before creating stationary frame parts.
 moving_objects=[o for o in group.objects if o not in fixed_parts]
 pivot=empty('LEAF_PIVOT',(-.06,side*.086,0));pivot['axis']='local Z';pivot['open_degrees']=side*100;pivot['logic']='none'
 for o in moving_objects:
  if o.parent is None:parent(o,pivot)
 # Frame/reveal outside exact clear width and height; 4 mm concealed rough-aperture gap.
 frame_mid=-side*wall_depth/2
 for x in [-.030,W+.030]:
  box('Reveal_Jamb',(x,frame_mid,H/2),(.060,wall_depth+.008,H),steel,.0006)
 box('Reveal_Header',(W/2,frame_mid,H+.030),(W+.120,wall_depth+.008,.060),steel,.0006)
 for face,edge in [(side,0),(-side,-side*wall_depth)]:
  # Wide cover trim bridges the cut core without occupying clear width.
  for x in [-.067,W+.067]:box('Jamb_Cover',(x,edge+face*.008,H/2),(.134,.008,H),blue,.001)
  box('Head_Cover',(W/2,edge+face*.008,H+.062),(W+.268,.008,.124),blue,.001)
 for x in [-.022,W+.022]:
  box('Seal_Stop_Channel',(x,side*.0155,H/2),(.022,.011,H),steel,.0006)
  box('Compression_Seal',(x,side*.023,H/2),(.014,.012,H),rubber,.001)
 box('Head_Stop_Channel',(W/2,side*.0155,H+.024),(W+.044,.011,.022),steel,.0006)
 box('Head_Seal',(W/2,side*.023,H+.024),(W+.030,.012,.012),rubber,.001)
 # Strike receiver clear of the aperture; a real cut socket in a separate keeper.
 strike=box('Strike_Keeper',(W+.031,center,1.1),(.022,.040,.095),ss,0)
 cut=box('TEMP_STRIKE',(W+.025,center,1.1),(.05,.022,.029),None,0);diff(strike,cut);bpy.data.objects.remove(cut,do_unlink=True);bevel(strike,.0004)
 # Flush threshold pan, top at Z=0, avoids sacrificing the 2.3/2.2 clear headroom.
 # Patch the underlying floor locally so the pan never doubles a visible floor face.
 pan=box('Flush_Threshold',(W/2,frame_mid,-.006),(W,.34,.012),ss,.001)
 floornames=(['FIT_Arrival_court_floor','FIT_Hall_Floor'] if spec['id']=='ARRIVAL' else ['FIT_Hall_Floor'] if spec['id']=='GONDOLA' else ['FIT_Arrival_court_floor','FIT_Coffee_Floor'])
 if spec['id']=='GONDOLA':
  # A short pan lip bridges onto the grating. Cut only the intersecting local bars.
  for ob in list(ref.objects):
   if not ob.name.startswith('PL03_Grate_'):continue
   vv=[T.inverted()@ob.matrix_world@Vector(p) for p in ob.bound_box]
   lo=[min(p[k] for p in vv) for k in range(3)];hi=[max(p[k] for p in vv) for k in range(3)]
   if lo[0]<W+.001 and hi[0]>-.001 and lo[1]<frame_mid+.171 and hi[1]>frame_mid-.171 and lo[2]<.001 and hi[2]>-.015:floornames.append(ob.name)
 for floorname in floornames:
  existing=next((o for o in s.objects if o.name==floorname or o.get('replaces_source_object')==floorname),None)
  assert existing is not None, floorname
  if not existing.get('replaces_source_object'):
   existing.data=existing.data.copy();existing['replaces_source_object']=floorname
   for c in list(existing.users_collection):c.objects.unlink(existing)
   patchcol.objects.link(existing);existing.name='PLD_PATCH_'+floorname
  tool=box('TEMP_PAN_POCKET',(W/2,frame_mid,-.007),(W+.002,.342,.016),None,0);tool.matrix_world=T;diff(existing,tool);bpy.data.objects.remove(tool,do_unlink=True)
  patches.append(dict(door=spec['id'],source_object=floorname,replacement_object=existing.name,operation='DIFFERENCE',local_box_center=[W/2,frame_mid,-.007],local_box_dimensions=[W+.002,.342,.016],matrix_world=[list(r) for r in T],purpose='flush pan pocket; 1 mm edge gap, 3 mm underside gap'))
 # Exterior drip head and weather closure placed beyond corrugation peaks.
 exterior_edge=0 if spec['id'] in {'STAFF','ARRIVAL'} else -side*wall_depth
 box('Drip_Head',(W/2,exterior_edge+ext*.052,H+.135),(W+.30,.100,.012),zinc,.001)
 box('Drip_Downstand',(W/2,exterior_edge+ext*.099,H+.120),(W+.30,.006,.030),zinc,.0005)
 # Closed position has bottom gasket at 10 mm above the flush pan; it drops to contact.
 base=bottom.location.copy()
 for frame,offset in [(1,-.010),(12,0),(40,0),(80,0)]:
  bottom.location=base+Vector((0,0,offset));bottom.keyframe_insert(data_path='location',frame=frame)
 # Animate latch release before leaf movement. These are Blender review poses only.
 base=latch.location.copy()
 for frame,offset in [(1,0),(12,-.014),(40,-.014),(80,-.014)]:
  latch.location=base+Vector((offset,0,0));latch.keyframe_insert(data_path='location',frame=frame)
 for frame,angle in [(1,0),(12,0),(40,45),(80,100)]:
  pivot.rotation_euler.z=math.radians(side*angle);pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
 s.frame_set(1)
 assembly=empty('ROOT',(0,0,0))
 for o in list(group.objects):
  if o!=assembly and o.parent is None:parent(o,assembly)
 assembly.matrix_world=T
 bpy.context.view_layer.update()
 record=dict(spec,root=assembly.name,matrix_world=[list(r) for r in T],hinge_pivot_local=[-.06,side*.086,0],hinge_pivot_station=list(T@Vector((-.06,side*.086,0))),leaf_dimensions_m=[W+.03,.045,H+.002],leaf_z_bounds_m=[.018,H+.020],hinge_heights_m=hinge_z,handle_height_m=1.1,cylinder_height_m=1.,hardware_scale=[1,1,1],full_open_degrees=side*100,threshold_top_m=0,glazing_thickness_m=.008,frames={'closed':1,'partly_open_45':40,'fully_open_100':80})
 manifest.append(record)
 print('ASSEMBLY_COMPLETE',spec['id'],flush=True)
print('DOORS_BUILT',flush=True)
s.frame_end=80;s.render.fps=24
for f,label in [(1,'CLOSED'),(12,'LATCH / BOTTOM SEAL RELEASE'),(40,'PARTLY OPEN 45'),(80,'FULLY OPEN 100')]:s.timeline_markers.new(label,frame=f)
group=review;prefix='PLD_REVIEW_'
def camera(n,p,target,ortho=None,lens=35):
 d=bpy.data.cameras.new(prefix+n);o=bpy.data.objects.new(prefix+n,d);review.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.03;d.clip_end=400
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
def light(n,p,target,power,size):
 d=bpy.data.lights.new(prefix+n,'AREA');o=bpy.data.objects.new(prefix+n,d);review.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.shape='DISK';d.size=size
views=[]
for d in manifest:
 T=Matrix(d['matrix_world']);W=d['width'];side=d['side'];H=d['height']
 def P(v):return T@Vector(v)
 for face in [-1,1]:
  cam=camera(d['id']+('_Face_A' if face<0 else '_Face_B'),P((W*.5,face*2.7,1.65)),P((W*.5,0,1.18)),lens=30)
  views.append(dict(name=d['id']+('_Face_A' if face<0 else '_Face_B'),camera=cam.name,frame=1))
  light(d['id']+'_Neutral_'+str(face),P((W*.5,face*1.5,2.7)),P((W*.5,0,1.1)),180,1.9)
  cam=camera(d['id']+'_Hardware_'+str(face),P((W-.38,face*.60+side*.0525,1.21)),P((W-.12,side*.0525,1.04)),lens=52)
  views.append(dict(name=d['id']+'_Hardware_'+str(face),camera=cam.name,frame=1))
 cam=camera(d['id']+'_Swing_Plan',P((W*.5,side*.55,9)),P((W*.5,side*.55,0)),ortho=4.8)
 for f,pose in [(1,'Closed'),(40,'Partial'),(80,'Open')]:views.append(dict(name=d['id']+'_Plan_'+pose,camera=cam.name,frame=f))
 cam=camera(d['id']+'_Fitted_Swing',P((W*.5,side*2.4,1.65)),P((W*.40,side*.3,1.1)),lens=25)
 for f,pose in [(40,'Partial'),(80,'Open')]:views.append(dict(name=d['id']+'_Fitted_'+pose,camera=cam.name,frame=f))
s.world=bpy.data.worlds.new('PLD_Neutral_Review_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.42,.46,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.frame_set(1);s.camera=bpy.data.objects[views[0]['camera']]
import runpy
runpy.run_path(str(OUT/'scripts/refine_bottom_seals.py'),run_name='pld_bottom_seals')['apply']()
inventory=[]
for o in assets.all_objects:
 inventory.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.location),rotation_euler=list(o.rotation_euler),scale=list(o.scale),dimensions=list(o.dimensions),matrix_world=[list(r) for r in o.matrix_world],materials=[m.name for m in o.data.materials] if o.type in {'MESH','FONT'} else []))
(OUT/'replacement_manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(OUT.parents[2])),source_sha256=EXPECTED,units='metres, Blender Z up',doors=manifest,objects=inventory,excluded_from_export=['PLD_REFERENCE_ONLY_Approved_Lodge','PLD_REFERENCE_ONLY_Removable_Roof','PLD_REVIEW_ONLY'],replaced_proxies=[d['proxy'] for d in DOORS],proxy_note='These were hidden sweep curves, not installed door leaves. Restroom curves are not replaced.',interaction='Blender pose animation only; no game logic or keypad'),indent=2))
(OUT/'wall_patches.json').write_text(json.dumps(dict(source_sha256=EXPECTED,patches=patches,scope='Only three door apertures and flush threshold footprints; apply to a copy, never master in this package.',merge_note='Shared floor objects contain multiple local pan cuts. Replay local cuts when merging with other packages, do not replace whole shared floor blindly.'),indent=2))
(OUT/'reference_transforms.json').write_text('[\n'+',\n'.join(json.dumps(r,separators=(',',':')) for r in ref_record)+'\n]')
(OUT/'review_views.json').write_text(json.dumps(views,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
print('BUILD_SAVED',flush=True)
