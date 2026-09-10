"""Build isolated delivery collection and source-fitted review copy. Blender 5.0."""
import bpy,math,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];SOURCE=Path(os.environ.get('MALDEK_SOURCE','C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'))
HASH=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert HASH=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
# Keep only the working scene in the review copy; source datablocks are independent.
for scene in list(bpy.data.scenes):
 if scene!=s:bpy.data.scenes.remove(scene)
s.name='PLG_Fitted_Review';s.unit_settings.system='METRIC'
ref=bpy.data.collections.new('REFERENCE_ONLY_Source_Context');s.collection.children.link(ref)
for c in list(s.collection.children):
 if c!=ref:s.collection.children.unlink(c);ref.children.link(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o);ref.objects.link(o)
ref['export']=False
retire=['FIT_Poster_frame_1','FIT_Poster_frame_2','FIT_Poster_frame_3','Service_lettering.001','FIT_Menu_placeholder']
for name in retire:
 o=bpy.data.objects.get(name)
 if o:o.hide_render=True;o.hide_set(True)
bpy.data.collections['PL03_Removable_Roof'].hide_render=True
col=bpy.data.collections.new('PLG_Wall_Details');s.collection.children.link(col)
review=bpy.data.collections.new('PLG_REVIEW_ONLY');s.collection.children.link(review)
roots=[];layers=[]
def material(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new('PLG_'+n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
pine=bpy.data.materials.get('PL03_Aged_Pine') or material('Pine',(.28,.16,.065))
metal=material('Petrol_enamel',(.045,.105,.12),.55,.35);steel=material('Galvanized_fasteners',(.38,.41,.4),.8,.28);paper=material('Paper_edges',(.79,.74,.60),0,.85);rubber=material('Gasket',(.018,.024,.023),0,.72);cork=material('Cork',(.26,.135,.06),0,.85);pinmat=material('Pin_ochre',(.55,.25,.055),.35,.4)
# Localized cork texture, explicitly Blender procedural (requires bake at integration).
nt=cork.node_tree;p=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=185; bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.0008;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
glass=material('Case_glass',(.96,.98,.98),0,.12);pg=glass.node_tree.nodes.get('Principled BSDF');pg.inputs['Transmission Weight'].default_value=1;pg.inputs['IOR'].default_value=1.45
# Licensed Cork001, real UV scale is one repeat/metre on board.
for channel,socket in [('Color','Base Color'),('Roughness','Roughness')]:
 node=nt.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(P/'materials'/'Cork001'/('Cork001_1K-JPG_'+channel+'.jpg')));im.pack();im.filepath='//materials/Cork001/'+im.name
 if channel!='Color':im.colorspace_settings.name='Non-Color'
 node.image=im
 if channel=='Color':
  tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=.72;tint.inputs[2].default_value=(.48,.30,.15,1);nt.links.new(node.outputs['Color'],tint.inputs[1]);nt.links.new(tint.outputs['Color'],p.inputs[socket])
 else:nt.links.new(node.outputs['Color'],p.inputs[socket])
textures={}
def tex(name):
 if name in textures:return textures[name]
 m=material('Ink_'+name,(.8,.8,.8),0,.74);n=m.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(P/'textures'/f'{name}.png'),check_existing=True);im.pack();im.filepath='//textures/'+name+'.png';n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);textures[name]=m;return m
def root(name,pos,u):
 o=bpy.data.objects.new('PLG_'+name,None);col.objects.link(o);u=Vector(u);v=Vector((0,0,1));n=u.cross(v);o.matrix_world=Matrix(((u.x,v.x,n.x,pos[0]),(u.y,v.y,n.y,pos[1]),(u.z,v.z,n.z,pos[2]),(0,0,0,1)));o['assembly_origin']='Back centre at mount plane; local X right, Y up, Z face normal';roots.append(o);return o
def box(name,parent,loc,dims,mat,bevel=0):
 vs=[(x*dims[0]/2,y*dims[1]/2,z*dims[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();o=bpy.data.objects.new('PLG_'+name,me);col.objects.link(o);o.parent=parent;o.location=loc
 uv=me.uv_layers.new(name='Surface_UV')
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x+0.5,v.y+0.5)
 o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Machined edge','BEVEL');mod.width=bevel;mod.segments=3
 return o
def face(name,parent,w,h,z,art,thick=.00035,curl=0):
 # Thin closed paper slab, grid front/back supports actual controlled corner curl.
 nx=16 if curl else 1;ny=16 if curl else 1;vs=[]
 for back in [0,1]:
  for j in range(ny+1):
   for i in range(nx+1):
    x=i/nx;y=j/ny;delta=curl*max(0,(x-.65)/.35)**2*max(0,(.35-y)/.35)**2;vs.append(((x-.5)*w,(y-.5)*h,z+delta-back*thick))
 stride=nx+1;N=(nx+1)*(ny+1);fs=[];front=[]
 for j in range(ny):
  for i in range(nx):
   a=j*stride+i;fs.extend([(a,a+1,a+1+stride,a+stride),(N+a+stride,N+a+1+stride,N+a+1,N+a)]);front.extend([True,False])
 perimeter=list(range(nx+1))+[j*stride+nx for j in range(1,ny+1)]+[ny*stride+i for i in range(nx-1,-1,-1)]+[j*stride for j in range(ny-1,0,-1)]
 for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):fs.append((a,N+a,N+b,b));front.append(False)
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('PLG_'+name,me);col.objects.link(o);o.parent=parent;me.materials.append(paper);me.materials.append(tex(art));uv=me.uv_layers.new(name='Artwork_0_1')
 for p,yes in zip(me.polygons,front):
  p.material_index=int(yes)
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x/w+.5,co.y/h+.5)
 o['artwork']=art;o['paper_thickness_m']=thick;o['max_corner_curl_m']=curl;return o
def cyl(name,parent,loc,r,depth,mat,axis='Z'):
 vs=[(r*math.cos(i*math.tau/32),r*math.sin(i*math.tau/32),z*depth/2) for z in [-1,1] for i in range(32)];fs=[tuple(range(31,-1,-1)),tuple(range(32,64))]+[(i,(i+1)%32,(i+1)%32+32,i+32) for i in range(32)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('PLG_'+name,me);col.objects.link(o);o.parent=parent;o.location=loc;me.materials.append(mat);me.uv_layers.new(name='Surface_UV')
 if axis=='Y':o.rotation_euler.x=math.pi/2
 mod=o.modifiers.new('Rounded edge','BEVEL');mod.width=min(depth/4,.001);mod.segments=2;return o
def screw(name,parent,x,y,z):
 cyl(name,parent,(x,y,z),.004,.003,steel);box(name+'_slot',parent,(x,y,z+.0016),(.005,.0008,.0003),rubber)
def framed(name,pos,u,w,h,art,mat=pine,glazed=False):
 r=root(name,pos,u);box(name+'_backboard',r,(0,0,.012),(w,h,.018),paper,.002)
 face(name+'_print',r,w-.06,h-.06,.025,art)
 dep=.060 if glazed else .037; rail=.027
 for x in [-1,1]:box(name+f'_side_{x}',r,(x*(w-rail)/2,0,dep/2),(rail,h,dep),mat,.002)
 for y in [-1,1]:box(name+f'_rail_{y}',r,(0,y*(h-rail)/2,dep/2),(w-2*rail,rail,dep),mat,.002)
 for x in [-w*.33,w*.33]:
  box(name+'_mount',r,(x,0,-.003),(.06,.12,.012),steel,.001);screw(name+'_mount_screw',r,x,.035,.007)
 if glazed:
  box(name+'_glass',r,(0,0,.044),(w-.060,h-.060,.002),glass,.0002)
  for x in [-w/2+.04,w/2-.04]:
   for y in [-h/2+.04,h/2-.04]:screw(name+'_retainer',r,x,y,.048)
 layers.append(dict(root=r.name,paper_front=.025,paper_back=.02465,backboard_front=.021,glass_back=.043 if glazed else None,surface_gap_m=.00365));r['display_size_m']=[w,h];r['mount_height_above_floor_m']=pos[2]-4;return r
for i,y in enumerate([1.425,-.575,-2.575],1):framed('Poster_'+str(i),(-23.901,y,5.675),(0,1,0),.75,1.05,'poster_'+str(i))
framed('Timetable',(-18.30,3.800,5.65),(1,0,0),.84,1.16,'timetable',metal,True)
framed('Visitor_map',(-10.30,.40,5.68),(0,-1,0),1.44,1.18,'visitor_map',metal,True)
r=root('Community',(-23.901,-4.8,5.66),(0,1,0));w=1.55;h=1.10
box('Community_back',r,(0,0,.013),(w,h,.022),pine,.003);box('Community_cork',r,(0,0,.029),(w-.04,h-.04,.010),cork,.001)
for x in [-1,1]:box('Community_side',r,(x*(w-.025)/2,0,.033),(.025,h,.042),pine,.002)
for y in [-1,1]:box('Community_rail',r,(0,y*(h-.025)/2,.033),(w-.05,.025,.042),pine,.002)
face('Community_heading',r,1.40,.12,.038,'notice_header',.001)
heading=bpy.data.objects['PLG_Community_heading'];heading.location.y=.44
# Five notices concentrated on left; right half remains usable for future evidence.
for i,(name,x,y) in enumerate([('club',-.57,.17),('lost',-.24,.16),('hours',-.58,-.21),('walk',-.25,-.20),('weather',.0,-.24)]):
 n=face('Notice_'+name,r,.27,.328,.040+i*.0007,'notice_'+name,curl=.004 if i in [1,4] else 0);n.location=(x,y,0);n.rotation_euler.z=math.radians([1,-2,-1,2,-3][i]);cyl('Pin_'+name,r,(x,y+.145,.050+i*.0007),.0055,.007,pinmat)
for x in [-.68,.68]:screw('Community_wall_fix',r,x,-.46,.042)
r['reserved_area_fraction']=.5;r['display_size_m']=[w,h]
# Fixed headers, all above opening clear heights. No leaf changes.
def plaque(name,pos,u,w,h,art):
 r=root(name,pos,u);box(name+'_enamel',r,(0,0,.009),(w,h,.012),metal,.004);face(name+'_art',r,w-.014,h-.014,.016,art,.0003)
 for x in [-w/2+.009,w/2-.009]:screw(name+'_fixing',r,x,0,.017)
 r['display_size_m']=[w,h];return r
plaque('Restrooms',(-15.10,-6.998,6.58),(-1,0,0),1.04,.22,'restrooms')
plaque('Public_exit',(-17.10,-6.998,6.60),(-1,0,0),1.06,.25,'exit')
plaque('Boarding',(-17.10,3.800,6.61),(1,0,0),1.04,.25,'boarding')
plaque('Women',(-13.65,-8.998,6.51),(-1,0,0),.68,.18,'women')
plaque('Men',(-11.65,-8.998,6.51),(-1,0,0),.68,.18,'men')
plaque('Staff',(-19.078,-10.5,6.52),(0,1,0),.82,.21,'staff')
# Artwork inserts only; no duplicate kitchen frames/counter/cubby.
r=root('Menu_insert',(-21.60,-6.968,6.53),(-1,0,0));face('Menu_artwork',r,2.07,.355,0,'menu',.0004)
r=root('Lost_property_insert',(-19.630,-6.596,5.156),(-1,0,0));face('Lost_property_artwork',r,.44,.055,0,'lost_property',.0004)
# Clock: separate hands pivot exactly at axle; static 10:10, no runtime status link.
r=root('Clock',(-23.895,-.575,6.65),(0,1,0));cyl('Clock_case',r,(0,0,.029),.185,.056,metal);cyl('Clock_dial',r,(0,0,.059),.165,.003,paper)
# Disc with radial UV, one front surface and no duplicate flat artwork slab.
o=bpy.data.objects['PLG_Clock_dial'];o.data.materials.append(tex('clock_face'));uv=o.data.uv_layers.active
for p in o.data.polygons:
 if p.normal.z>.5:
  p.material_index=1
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.33+.5,v.y/.33+.5)
for name,length,width,z,angle in [('Hour',.088,.009,.065,-55),('Minute',.128,.006,.071,-60)]:
 pivot=bpy.data.objects.new('PLG_Clock_'+name+'_pivot',None);col.objects.link(pivot);pivot.parent=r;pivot.location.z=z;pivot.rotation_euler.z=math.radians(55 if name=='Hour' else angle)
 box('Clock_'+name+'_hand',pivot,(0,length/2,0),(width,length,.003),rubber,.001);pivot['motion']='Static dressing; local Z axle, no status system'
cyl('Clock_axle',r,(0,0,.076),.010,.010,steel)
exec(compile((P/'scripts'/'weathering.py').read_text(),str(P/'scripts'/'weathering.py'),'exec'))
# Persist source references and object inventory before producing delivery-only blend.
bpy.context.view_layer.update()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
manifest={'source_sha256':HASH,'source_file':str(SOURCE),'units':'metres Z up','assembly_convention':'Each PLG root uses documented world matrix; child X right, Y up, Z forward. Source local layout maps (x-24.1,-depth+4,z+4).','collection':col.name,'retire_exact':retire,'legacy_recommendation':{'object':'Service_lettering.001','body':'MALDEK / ARRIVALS','action':'Retire obsolete reversed interior label at integration; preserve Service_lettering and gondola status sign.'},'wall_patches':[],'surface_layers':layers,'objects':[dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,dimensions=list(o.dimensions),matrix_world=[list(row) for row in o.matrix_world],bounds=bounds(o) if o.type=='MESH' else None,materials=[m.name for m in o.data.materials] if o.type=='MESH' else [],artwork=o.get('artwork')) for o in col.objects], 'kitchen_artwork':{'menu':{'replaces_text':'PLK_Menu_Editable','retains':['PLK_Menu_Board','PLK_Menu_Frame'],'size_m':[2.07,.355],'world_centre':[-21.6,-6.968,6.53]},'lost_property':{'replaces_text':'PLK_Cubby_Label','retains':['PLK_Cubby_Label_strip'],'size_m':[.44,.055],'world_centre':[-19.63,-6.596,5.156]}},'export_exclude':['REFERENCE_ONLY_Source_Context','PLG_REVIEW_ONLY'],'editorial':['Printed 09:00 / 30-minute / 16:30 timetable is provisional fiction; confirm story operating schedule.','No prices, currencies or dated event commitments are printed.','Poster landscapes are decorative invented geography, not a piste map.','Five community notices and menu choices are proposed editorial dressing.','Critical ticket wording is not reproduced; no ticket/key/bag/locker assets owned.','Coat hooks omitted to retain blank wall and avoid circulation crowding.'],'limitations':['Blender proxy clearance checks only; no Unreal import or collision/PIE verification.','Source furniture and fittings remain reference proxies.','Reused pine and cork bump use Blender procedural nodes; bake at integration. Cork color and roughness are CC0 image maps.','Cases have removable screw-retained glazing; no hinged opening or animation claimed.']}
(P/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
# Useful reusable review cameras and temporary lighting.
views=[('01_West_cluster',(-19.7,-.575,5.65),(-23.90,-.575,5.85),24),('02_Timetable_close',(-18.3,2.15,5.65),(-18.3,3.77,5.65),34),('03_Map_close',(-12.4,.4,5.68),(-10.33,.4,5.68),45),('04_Community_close',(-22.0,-4.8,5.66),(-23.87,-4.8,5.66),42),('05_Restroom_approach',(-16.4,-4.8,5.65),(-14.95,-7.1,6.0),34),('06_Hall_eye',(-17.1,-6.35,5.65),(-18.3,1.5,5.8),20),('07_Hall_service',(-21.8,1.8,5.65),(-16.5,-6.7,5.8),23),('08_Wayfinding_hall',(-15.1,-8.18,5.65),(-12.65,-9.02,6.25),24),('09_West_walk',(-20.3,-4.5,5.65),(-23.90,-2.1,5.75),25),('10_Clock_close',(-22.8,-.575,6.65),(-23.89,-.575,6.65),53),('11_Overview',(-17.1,-1.6,18),(-17.1,-1.6,4),35)]
for name,pos,target,lens in views:
 d=bpy.data.cameras.new('PLG_REVIEW_'+name);o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.035
 if name=='11_Overview':d.type='ORTHO';d.ortho_scale=17
for i,(x,y) in enumerate([(-21,1),(-15,1),(-21,-4),(-15,-4),(-13,-8.1),(-21.6,-8.5)]):
 d=bpy.data.lights.new('PLG_TEMP_NEUTRAL_'+str(i),'AREA');d.energy=180;d.shape='DISK';d.size=3;d.color=(1,.94,.84);o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=(x,y,7.0)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.camera=bpy.data.objects['PLG_REVIEW_06_Hall_eye'];s.world.color=(.16,.16,.16)
# Append only the exact kitchen context needed to evaluate supplied inserts, if available.
kpath=SOURCE.parent.parent/'passenger_lodge_kitchen_01'/'Maldek_Passenger_Lodge_Kitchen.blend'
if kpath.exists():
 with bpy.data.libraries.load(str(kpath),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('PLK_Menu') or n.startswith('PLK_Cubby') or n=='PLK_Lost_property' or n=='PLK_Assembly']
 for o in dst.objects:
  if o:
   ref.objects.link(o)
   if o.name.startswith(('PLK_Menu_Editable','PLK_Cubby_Label')) and o.type=='FONT':o.hide_render=True
s['review_note']='Temporary lights and reference context excluded from delivery. Roof hidden only in fitted copy.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Wall_Details_Fitted.blend'))
# New scene includes only package and review rig. Remove reference scenes then orphan purge.
delivery=bpy.data.scenes.new('PLG_Delivery');delivery.collection.children.link(col);delivery.unit_settings.system='METRIC';bpy.context.window.scene=delivery
bpy.data.scenes.remove(s)
# Unlink/delete all objects except owned delivery objects (reference-only data never exported).
keep=set(col.objects)
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c!=col:bpy.data.collections.remove(c)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Wall_Details.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==HASH
print('PACKAGE_BUILT',len(col.objects))
