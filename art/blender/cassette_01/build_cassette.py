"""Original station audio cassette, authored at real scale. Blender review only; no Unreal import."""
import bpy, math, random, json, bmesh
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
random.seed(147)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'
MM=.001
asset=bpy.data.collections.new('CASSETTE / editable parts');scene.collection.children.link(asset)
stage=bpy.data.collections.new('STUDIO / review only');scene.collection.children.link(stage)
def move_collection(obj,collection=asset):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 collection.objects.link(obj)
def mat(name,color,metal=0,rough=.4,noise=False,transmission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.48
 if noise:
  tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4800;tex.inputs['Detail'].default_value=2.5
  bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00004
  links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
  ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=tuple(v*.68 for v in color)+(1,)
  ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=tuple(min(1,v*1.12) for v in color)+(1,)
  links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 return m
shell=mat('01 / moulded charcoal ABS',(.021,.03,.027),rough=.4,noise=True)
edge=mat('02 / edge patina',(.068,.083,.069),rough=.52,noise=True)
ivory=mat('03 / aged paper',(.69,.61,.425),rough=.83,noise=True)
orange=mat('04 / faded oxide orange',(.48,.105,.036),rough=.76,noise=True)
ink=mat('05 / warm black print',(.013,.018,.014),rough=.66)
hubmat=mat('06 / acetal reel hubs',(.64,.66,.54),rough=.32,noise=True)
tape=mat('07 / ferric oxide magnetic tape',(.063,.025,.011),metal=.18,rough=.31)
tapeedge=mat('08 / wound tape edge',(.11,.049,.018),metal=.12,rough=.5)
steel=mat('09 / screw steel',(.38,.42,.4),metal=.92,rough=.3,noise=True)
dark=mat('10 / cavity shadow',(.007,.009,.008),rough=.72)
glass=mat('11 / smoked polycarbonate window',(.32,.4,.33),rough=.12,transmission=.92)
felt=mat('12 / pressure pad felt',(.17,.12,.072),rough=.98,noise=True)
floor_mat=mat('Studio slate',(.024,.03,.031),rough=.64,noise=True)

def finish(o,name,material=None):
 o.name=name;move_collection(o)
 if material:o.data.materials.append(material)
 return o
def bevel(o,width=.12,segments=3):
 m=o.modifiers.new('Small moulded edge radius','BEVEL');m.width=width*MM;m.segments=segments
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
def box(name,loc,size,material,bevel_mm=.1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)*MM);o=bpy.context.object;o.dimensions=Vector(size)*MM
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,material)
 if bevel_mm:bevel(o,bevel_mm)
 return o
def panel(name,loc,w,h,d,r,material):
 x,y,z=loc;pts=[]
 for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for i in range(9):
   a=math.radians(start+i*90/8);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
 n=len(pts);verts=[((px+x)*MM,(y+side*d/2)*MM,(pz+z)*MM) for side in [-1,1] for px,pz in pts]
 faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);asset.objects.link(o)
 if material:mesh.materials.append(material)
 return o
def cylinder(name,loc,radius,depth,material,vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius*MM,depth=depth*MM,location=Vector(loc)*MM,rotation=(math.pi/2,0,0))
 o=finish(bpy.context.object,name,material)
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 return o
def cut(obj,cutter):
 bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new('Physical opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def path(name,points,material,radius=.06,cyclic=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=radius*MM;c.bevel_resolution=2
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*[v*MM for v in co],1)
 s.use_cyclic_u=cyclic
 o=bpy.data.objects.new(name,c);asset.objects.link(o);c.materials.append(material)
 return o
def annulus(name,x,z,outer,inner,depth,material,teeth=False,y=0,n=144):
 verts=[]
 for sy,r in [(-1,outer),(-1,inner),(1,outer),(1,inner)]:
  for i in range(n):
   a=2*math.pi*i/n;ri=r
   if teeth and r==inner and i%24 in range(8,17):ri-=1.3
   verts.append(((x+ri*math.cos(a))*MM,(y+sy*depth/2)*MM,(z+ri*math.sin(a))*MM))
 faces=[]
 for i in range(n):
  j=(i+1)%n
  faces.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(i,2*n+i,2*n+j,j),(n+j,3*n+j,3*n+i,n+i)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);asset.objects.link(o);mesh.materials.append(material)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 return o
font_regular=bpy.data.fonts.load('C:/Windows/Fonts/consola.ttf')
font_bold=bpy.data.fonts.load('C:/Windows/Fonts/consolab.ttf')
font_hand=bpy.data.fonts.load('C:/Windows/Fonts/consolai.ttf')
def text(name,body,x,y,z,size,material,back=False,bold=False,hand=False,align='LEFT'):
 bpy.ops.object.text_add(location=Vector((x,y,z))*MM,rotation=(math.pi/2,0,math.pi if back else 0))
 o=bpy.context.object;o.data.body=body;o.data.size=size*MM;o.data.align_x=align;o.data.extrude=.005*MM;o.data.resolution_u=5
 o.data.font=font_hand if hand else font_bold if bold else font_regular
 return finish(o,name,material)

# Two independently editable shell halves. The seam is an actual gap, not a painted line.
halves=[]
for side in [-1,1]:
 wall=panel(('A' if side<0 else 'B')+' / perimeter half',(0,side*2.34,31.9),100.4,63.8,4.48,2.3,shell)
 cut(wall,panel('Interior cavity',(0,0,31.9),96.4,59.8,20,1.5,None));halves.append(wall)
 face=panel(('A' if side<0 else 'B')+' / face plate',(0,side*5.15,31.9),100.4,63.8,1.12,2.3,shell)
 cut(face,panel('Reel viewing aperture',(0,side*5.15,35.5),75,25,8,5.2,None))
 window=panel(('A' if side<0 else 'B')+' / clear reel window',(0,side*5.14,35.5),74.7,24.7,.9,5.1,glass)
 for x in [-21.25,21.25]:cut(window,cylinder('Spindle access cutter',(x,0,35.5),11.2,20,None))
 halves.append(face)
 # Label edges remain visible around the central aperture.
 label=panel(('A' if side<0 else 'B')+' / paper label',(0,side*5.79,38.2),91,43,.13,1.15,ivory)
 cut(label,panel('Label window cutout',(0,side*5.79,35.5),76,26,4,5.6,None))
 # Moulded alignment and capstan holes below the label.
 for x,r in [(-31,2.05),(-18,1.25),(18,1.25),(31,2.05)]:cut(face,cylinder('Capstan opening',(x,0,7),r,20,None))
 # Authentic lower trapezoid shoulder, open underneath for the heads and rollers.
 pts=[(-34,0),(34,0),(29.5,13),(-29.5,13)];verts=[]
 for sy in [side*5.6,side*6.05]:verts += [(x*MM,sy*MM,z*MM) for x,z in pts]
 faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new('Bridge');me.from_pydata(verts,[],faces);me.update()
 bridge=bpy.data.objects.new(('A' if side<0 else 'B')+' / lower shoulder',me);asset.objects.link(bridge);me.materials.append(shell)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for x,r in [(-31,2.05),(-18,1.25),(18,1.25),(31,2.05)]:cut(bridge,cylinder('Shoulder capstan',(x,0,7),r,20,None))
 halves.append(bridge)
 # Five screw positions: four corners and one central bridge screw.
 for index,(x,z) in enumerate([(-46,59),(46,59),(-46,4.5),(46,4.5),(0,11)]):
  cut(face,cylinder('Screw recess',(x,side*5.45,z),2.0,1.0,None))
  if index==4:cut(bridge,cylinder('Bridge screw recess',(x,side*6.0,z),2.0,1.2,None))
  screw_y=5.8 if index==4 else 5.35
  head=cylinder(f'{side} / screw {index+1}',(x,side*screw_y,z),1.6,.5,steel,32)
  cut(head,box('Screwdriver slot',(x,side*(screw_y+.27),z),(2.45,.25,.32),None,0))
  if side<0:cut(head,box('Cross slot',(x,side*(screw_y+.27),z),(.32,.25,2.0),None,0))
  bevel(head,.07,2)
 # Label design is original, with readable printing on both sides.
 sy=side*5.88;back=side>0;mirror=-1 if back else 1
 box(f'{side} / orange archive stripe',(0,side*5.875,53.4),(88,.015,2.2),orange,.006)
 text(f'{side} / MILLFORD','MILLFORD',mirror*-42,sy,56.2,4.2,ink,back,True)
 text(f'{side} / C60','C60',mirror*32,sy,55.7,4.8,ink,back,True)
 text(f'{side} / archive line','STATION SERVICE  /  FIELD RECORDING',mirror*-42,side*5.903,52.9,1.6,ivory,back,True)
 text(f'{side} / side identifier','A' if side<0 else 'B',mirror*-42,sy,18.1,5.0,ink,back,True)
 text(f'{side} / handwritten title','NIGHT SHIFT - 14.11.86' if side<0 else 'RETURN TO CONTROL ROOM',mirror*-32,sy,20.7,2.65,ink,back,hand=True)
 text(f'{side} / serial','ARCHIVE 0147  /  DO NOT ERASE' if side<0 else 'MILLFORD OPERATIONS  /  30 MIN',mirror*-32,sy,17.6,1.55,ink,back)
 for z in [48.8,19.8]:path(f'{side} / ruled label',[(mirror*-32,side*5.896,z),(mirror*42,side*5.896,z)],orange,.025)
 # Fine lower grip ridges, intentionally stopping short of tape apertures.
 for x in [-39,-37,-35,35,37,39]:box(f'{side} / grip rib',(x,side*5.82,9),( .45,.22,7.5),edge,.09)
 text(f'{side} / moulded type','NORMAL BIAS  120 us',0,side*6.09,8.7,1.25,edge,back,align='CENTER')

# Open head, erase, and pinch-roller ports along the bottom edge.
for part in halves:
 for x,w in [(-27,7.8),(-14,6),(0,12),(14,6),(27,7.8)]:
  cut(part,box('Tape head clearance',(x,0,1.6),(w,20,4.3),None,0))

# Break-out recording tabs on the top edge: one intact, one visibly removed.
for side in [-1,1]:
 wall=halves[0 if side<0 else 3]
 # Select by name because each half includes face + shoulder.
 wall=next(o for o in asset.objects if o.name==('A' if side<0 else 'B')+' / perimeter half')
 for x in [-39,39]:cut(wall,box('Record protection pocket',(x,0,63),(6.2,6.8,3.2),None,0))
box('Record-protect tab / intact',(-39,0,62.75),(5.9,6.6,.5),shell,.12)
box('Broken tab / remaining stump',(41.3,0,61.8),(.8,6.5,.45),edge,.08)

# Real through-holes and six drive teeth in each reel, with unequal tape pack diameters.
for name,x,radius in [('Supply',-21.25,23.6),('Take-up',21.25,15.3)]:
 hub=annulus(name+' / six-tooth hub',x,35.5,10.65,6.1,4.6,hubmat,teeth=True)
 bevel(hub,.07,2)
 annulus(name+' / magnetic tape pack',x,35.5,radius,10.7,3.81,tape)
 for side in [-1,1]:
  for j in range(34):
   r=10.95+(radius-11)*j/33
   points=[(x+r*math.cos(i*math.tau/128),side*1.918,35.5+r*math.sin(i*math.tau/128)) for i in range(128)]
   path(name+' / tape winding',points,tapeedge,.012,True)
  for i in range(6):
   a=math.tau*i/6
   mark=box(name+' / hub mould mark',(x+8.3*math.cos(a),side*2.325,35.5+8.3*math.sin(a)),(2.2,.08,.38),edge,.03)
   mark.rotation_euler[1]=-a
for x in [-43,43]:
 cylinder('Tape guide roller',(x,0,7),3.3,4.4,hubmat)
 cylinder('Guide roller pin',(x,0,7),.95,9.1,steel,24)
for x in [-46,46]:
 for z in [4.5,59]:
  annulus('Internal screw boss',x,z,2.9,1.7,8.8,shell,n=32)
# Tape ribbon along its playable edge. It is a mesh strip, not a cylindrical cable.
route=[(-42,23),(-46,10),(-46,7),(-44.7,4.5),(-42,3.65),(-28,3.65),(-14,3.65),(0,3.65),(14,3.65),(28,3.65),(42,3.65),(44.7,4.5),(46,7),(45,12),(34,29)]
verts=[(x*MM,y*MM,z*MM) for x,z in route for y in [-1.905,1.905]]
faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(route)-1)]
me=bpy.data.meshes.new('3.81 mm magnetic ribbon');me.from_pydata(verts,[],faces);me.materials.append(tape)
o=bpy.data.objects.new('Exposed magnetic tape path',me);asset.objects.link(o)
mod=o.modifiers.new('Tape thickness / 0.017 mm','SOLIDIFY');mod.thickness=.017*MM
box('Pressure pad spring',(0,0,5.7),(14,3.8,.19),steel,.04)
box('Pressure pad felt',(0,0,4.75),(5.6,3.5,1.45),felt,.18)
box('Head shielding plate',(0,0,9.5),(15,5,.5),steel,.07)

# Restrained wear: small edge scuffs and label rubs, kept off the readable title.
for side in [-1,1]:
 for i in range(26):
  x=random.uniform(-44,44);z=random.choice([17,59])+random.uniform(-.25,.25)
  length=random.uniform(.25,1.3)
  path(f'{side} / paper-edge rub',[(x,side*5.904,z),(x+length,side*5.904,z+random.uniform(-.07,.07))],orange if i%5==0 else edge,.018)
 for i in range(20):
  x=random.choice([-48.5,48.5])+random.uniform(-.1,.1);z=random.uniform(15,56)
  path(f'{side} / ABS edge scuff',[(x,side*5.719,z),(x+random.uniform(-.1,.1),side*5.719,z+random.uniform(.3,1.7))],edge,.023)

# All normals corrected before save; components remain named and editable.
for obj in asset.objects:
 if obj.type=='MESH':
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
  for p in obj.data.polygons:p.use_smooth=False
root=bpy.data.objects.new('CASSETTE / 100.4 x 63.8 mm',None);asset.objects.link(root)
for obj in list(asset.objects):
 if obj!=root:obj.parent=root
root['status']='BLENDER REVIEW ONLY - awaiting approval before Unreal placement'
root['dimensions_mm']='100.4 wide x 63.8 tall x approximately 12.1 deep'
root['reel_spacing_mm']=42.5;root['tape_width_mm']=3.81

# Studio setup and saved cameras.
bpy.ops.mesh.primitive_plane_add(size=2000*MM,location=(0,0,-.45*MM));ground=bpy.context.object;ground.name='Studio / ground';move_collection(ground,stage);ground.data.materials.append(floor_mat)
def camera(name,loc,target,ortho):
 bpy.ops.object.camera_add(location=Vector(loc)*MM);c=bpy.context.object;c.name=name;move_collection(c,stage)
 c.rotation_euler=(Vector(target)*MM-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=ortho*MM;c.data.clip_start=.001;c.data.clip_end=20
 return c
cameras={
 '01_hero':camera('REVIEW / front three quarter',(118,-220,108),(0,0,31),140),
 '02_front':camera('REVIEW / face A',(0,-240,32),(0,0,32),123),
 '03_back':camera('REVIEW / face B',(-105,220,88),(0,0,32),139),
 '04_tape_edge':camera('REVIEW / tape head ports',(80,-150,-36),(0,0,12),120),
}
def light(name,loc,power,size,color,target=(0,0,30)):
 bpy.ops.object.light_add(type='AREA',location=Vector(loc)*MM);o=bpy.context.object;o.name=name;move_collection(o,stage)
 o.data.energy=power;o.data.shape='DISK';o.data.size=size*MM;o.data.color=color
 o.rotation_euler=(Vector(target)*MM-o.location).to_track_quat('-Z','Y').to_euler()
light('Studio / large key',(-95,-120,170),8,130,(1,.89,.73))
light('Studio / cool fill',(130,-70,65),3,105,(.69,.82,1))
light('Studio / edge strip',(30,105,145),10,100,(1,.72,.42))
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.07,.08,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for device in prefs.devices:device.use=device.type!='CPU'
 scene.cycles.device='GPU'
except Exception:scene.cycles.device='CPU'
scene.render.resolution_x=1800;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-3
scene.camera=cameras['01_hero']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.clip_start=.001;area.spaces.active.clip_end=100
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Millford_Service_Cassette.blend'))
report={'status':'Blender review only; not imported or placed in Unreal','scale':'metres','width_mm':100.4,'height_mm':63.8,'depth_mm':12.1,'reel_centres_mm':42.5,'tape_width_mm':3.81,'parts':len(asset.objects),'mesh_vertices':sum(len(o.data.vertices) for o in asset.objects if o.type=='MESH'),'references':['https://www.duplication.com/cassette-selection-guide.php','https://www.recordingthemasters.com/blank-cassettes'],'renders':[]}
for name,cam in cameras.items():
 scene.camera=cam;ground.hide_render=name=='04_tape_edge'
 scene.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);report['renders'].append(scene.render.filepath)
scene.camera=cameras['01_hero'];ground.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Millford_Service_Cassette.blend'))
(OUT/'build_report.json').write_text(json.dumps(report,indent=2))
