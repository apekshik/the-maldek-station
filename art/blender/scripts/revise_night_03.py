"""Load saved revision02 in background; create revision03 without changing earlier files."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix,noise
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'revision_03';(OUT/'previews').mkdir(exist_ok=True)
scene=bpy.context.scene
full=scene.view_layers['02_Full_Shell'];bpy.context.window.view_layer=full
for lc in full.layer_collection.children:lc.exclude=False
C={c.name:c for c in scene.collection.children}
def col(n):
 if n not in C:C[n]=bpy.data.collections.new(n);scene.collection.children.link(C[n])
 return C[n]
def remove(o):bpy.data.objects.remove(o,do_unlink=True)
def meshob(n,v,f,c,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);col(c).objects.link(o)
 if m:me.materials.append(m)
 o['export_geometry']=False;o['collision']=False;return o
def cube(n,p,s,c,m):
 x,y,z=s;v=[(a*x/2,b*y/2,d*z/2) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=meshob(n,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],c,m);o.location=p;return o
def beam(n,a,b,w,c,m):
 a,b=Vector(a),Vector(b);o=cube(n,(a+b)/2,(w,w,(b-a).length),c,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mat(n,color,rough=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
steel=bpy.data.materials['R02_Chipped_Painted_Steel'];concrete=bpy.data.materials['R02_Weathered_Concrete'];soil=bpy.data.materials['R02_Cliff_Rock_and_Forest_Soil']
# Smooth connected paths and a relocated relay.
for o in list(scene.objects):
 if o.name.startswith(('Fuel_To_Relay','Relay_To_Overlook','Forest_Pine','Cable_Ascending')):remove(o)
for o in list(scene.objects):
 if o.name.startswith(('Relay_Floor','Relay_South','Relay_North','Relay_Side','Relay_Cabinet','Relay_Roof','Relay_Warmth')):o.matrix_world=Matrix.Translation((22,12,1))@o.matrix_world
 if o.name.startswith('Bedrock_Pad') and o.location.x>20:remove(o)
def spline(points,steps=18):
 q=[Vector(points[0])]+[Vector(p) for p in points]+[Vector(points[-1])];r=[]
 for i in range(1,len(q)-2):
  a,b,c,d=q[i-1:i+3]
  for j in range(steps):
   t=j/steps;r.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
 return r+[tuple(points[-1])]
paths=[spline([(14,-6,0),(20,-8,.2),(30,-5,1.1),(40,2,2),(48,8,3),(48,11,3)]),spline([(48,15,3),(47,22,3.5),(38,25,4.3),(29,21,4.5),(22,14,4.1),(19,8,4),(15,5,4)])]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def nearest(x,y,pts):
 best=(1e9,0)
 for a,b in zip(pts,pts[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));d=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
  if d<best[0]:best=(d,a[2]+t*(b[2]-a[2]))
 return best
stairs=json.loads((BASE/'revision_02/blockout_dimensions.json').read_text())['stairs']
grades=paths+[[(st['x'],st['y0'],st['z0']),(st['x'],st['y1'],st['z1'])] for st in stairs]
pads=[(-15,-8,-6,0,3.60),(-8,-3,-4,0,3.60),(-2,6,-6,0,-.34),(8,15,-6,0,-.34),(46,50,11,15,2.66),(-21,-13,-18,-12,-1.34)]
def height(x,y):
 n=noise.noise(Vector((x*.045,y*.045,1.7)));detail=noise.noise(Vector((x*.2,y*.2,2.4)))
 west=4*(1-smooth(-18,-6,x));east=2*smooth(10,25,x)
 gorge=(1-smooth(7,17,abs(x-1)))*smooth(2,16,y)
 h=-.5+west+east+1.7*n+.35*detail-23*gorge
 # Continuous east shoulder replaces the crater beneath the former relay loop.
 if x>12:
  shoulder=.1+3.5*smooth(-4,10,y)+1.7*math.exp(-((x-35)**2+(y-10)**2)/90)
  w=smooth(12,20,x)*(1-smooth(32,45,y));h=h*(1-w)+shoulder*w
 for x0,x1,y0,y1,z in pads:
  d=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1));w=1-smooth(0,3,d);h=h*(1-w)+z*w
 for k,path in enumerate(grades):
  d,z=nearest(x,y,path);w=1-smooth(1.15,3.6,d);target=z-(.10 if k<2 else .38);h=h*(1-w)+target*w
 if -2<=x<=6 and 0<=y<=2:h=min(h,-.34)
 return h
old=bpy.data.objects['Terrain_Cliff_And_Relay_Spur'];remove(old)
nx=191;ny=181;v=[(-75+i,-65+j,height(-75+i,-65+j)) for j in range(ny) for i in range(nx)];f=[]
for j in range(ny-1):
 for i in range(nx-1):a=j*nx+i;f.append((a,a+1,a+nx+1,a+nx))
o=meshob('Terrain_Cliff_And_Relay_Spur',v,f,'15_Terrain',soil)
for p in o.data.polygons:p.use_smooth=True
pathmat=mat('R03_Wet_Gravel',(.055,.065,.048),.3)
for k,path in enumerate(paths):
 vs=[];fs=[]
 for i,p in enumerate(path):
  tangent=Vector(path[min(i+1,len(path)-1)])-Vector(path[max(0,i-1)]);side=Vector((-tangent.y,tangent.x,0)).normalized()
  for w in [-1,1]:vs.append(tuple(Vector(p)+side*w+Vector((0,0,-.015))))
 for i in range(len(path)-1):a=i*2;fs.append((a,a+2,a+3,a+1))
 o=meshob('Continuous_Relay_Path_'+str(k),vs,fs,'09_Relay_and_Paths',pathmat);o['collision']=True
 for p in o.data.polygons:p.use_smooth=True
# Textured CC0 pine variants, linked mesh instances. Import the authored LOD2 objects only.
asset=OUT/'assets/pine_tree_01_1k.blend'
with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in ['pine_tree_01_a_LOD2','pine_tree_01_b_LOD2','pine_tree_01_c_LOD2']]
protos=dst.objects
for im in bpy.data.images:
 if im.source=='FILE' and 'pine_tree' in im.filepath:
  p=OUT/'assets/textures'/Path(im.filepath).name
  if p.exists():im.filepath=str(p);im.reload();im.pack()
for p in protos:
 print('TREE',p.name,len(p.data.vertices),tuple(p.dimensions),flush=True)
# Bake mesh transforms relative to its own ground center and normalize to 16m.
for p in protos:
 me=p.data.copy();me.transform(p.matrix_world);zs=[v.co.z for v in me.vertices];xs=[v.co.x for v in me.vertices];ys=[v.co.y for v in me.vertices];origin=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,min(zs)));factor=16/(max(zs)-min(zs))
 for vert in me.vertices:vert.co=(vert.co-origin)*factor
 p.data=me
rng=random.Random(303);count=0
for attempt in range(4000):
 if count>=340:break
 x=rng.uniform(-64,100);y=rng.uniform(-45,103)
 if -24<x<20 and -22<y<16:continue
 if 44<x<53 and 8<y<18:continue
 if any(nearest(x,y,p)[0]<2.8 for p in paths):continue
 if abs(x)<10 and y>4:continue
 if 12<x<30 and 12<y<35:continue
 o=bpy.data.objects.new('Pine_CC0_'+str(count),protos[count%3].data);col('16_Forest').objects.link(o);o.location=(x,y,height(x,y)-.08);s=rng.uniform(.65,1.3);o.scale=(s,s,s*rng.uniform(.88,1.1));o.rotation_euler[2]=rng.random()*math.tau;count+=1
# Distant valley ridges and Maldek silhouette, 380m along the line.
def farheight(x,y):return -24+82*smooth(110,380,y)+abs(x)*.14+7*noise.noise(Vector((x*.018,y*.018,1)))
nx=91;ny=87;vs=[(-225+i*5,110+j*5,farheight(-225+i*5,110+j*5)) for j in range(ny) for i in range(nx)];fs=[]
for j in range(ny-1):
 for i in range(nx-1):a=j*nx+i;fs.append((a,a+1,a+nx+1,a+nx))
o=meshob('Distant_Valley_Ridges',vs,fs,'19_Cable_Route',soil)
for p in o.data.polygons:p.use_smooth=True
for i in range(260):
 x=rng.uniform(-210,210);y=rng.uniform(120,500)
 if abs(x)<15:continue
 o=bpy.data.objects.new('Distant_Pine_'+str(i),protos[i%3].data);col('16_Forest').objects.link(o);o.location=(x,y,farheight(x,y));s=rng.uniform(.8,1.6);o.scale=(s,s,s);o.rotation_euler.z=rng.random()*math.tau
for p in protos:remove(p)
for y,top in [(95,22),(225,43),(380,76)]:
 bottom=height(0,y) if y<110 else farheight(0,y)
 for x in [-3,3]:beam('Cable_Pylon',(x,y,bottom),(x*.5,y,top),.45,'19_Cable_Route',steel)
 beam('Pylon_Crosshead',(-4,y,top),(4,y,top),.42,'19_Cable_Route',steel)
for x in [-.9,.9]:
 pts=[(x,8,8),(x,95,22),(x,225,43),(x,380,76)]
 for a,b in zip(pts,pts[1:]):
  prev=Vector(a)
  for j in range(1,25):
   t=j/24;p=Vector(a).lerp(Vector(b),t);p.z-=2.5*4*t*(1-t);beam('Sagging_Cable',prev,p,.045,'19_Cable_Route',steel);prev=p
cube('Maldek_Remote_Terminal',(0,390,67),(22,22,14),'19_Cable_Route',concrete)
cube('Maldek_Observation_Tower',(10,395,81),(5,6,20),'19_Cable_Route',concrete)
cube('Maldek_Roof',(0,390,75),(25,25,.5),'19_Cable_Route',steel)
# Wet surfaces: varying low roughness and a clear water coat, retaining existing color maps.
for name in ['R02_Weathered_Concrete','R02_Chipped_Painted_Steel','R02_Oxide_Red_Sheet_Steel','R02_Galvanized_Grating']:
 m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED')
 for link in list(p.inputs['Roughness'].links):l.remove(link)
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.7;tex.inputs['Detail'].default_value=3
 geo=n.new('ShaderNodeNewGeometry');l.new(geo.outputs['Position'],tex.inputs['Vector']);r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.075;r.inputs['To Max'].default_value=.32;l.new(tex.outputs['Fac'],r.inputs['Value']);l.new(r.outputs['Result'],p.inputs['Roughness']);p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.09
# Night lighting; retain visible forms with cool moonlight and warm practical lamps.
for o in scene.objects:
 if o.type=='LIGHT':
  if o.data.type=='SUN':o.data.energy=.12
  elif o.name=='Sky_Fill':o.data.energy=850
  elif o.name=='Cliff_Bounce':o.data.energy=180
for n in scene.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=.045;n.inputs['Color'].default_value=(.13,.22,.36,1)
def light(n,loc,target,power,color,size=1):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);col('92_Cameras_Lights').objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
em=mat('R03_Lamp_Glow',(.7,.8,.85));p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.65,.8,1,1);p.inputs['Emission Strength'].default_value=6
for i,(x,y,z) in enumerate([(-2.7,4,6.9),(2.9,7.7,6.9),(4.7,10.3,6.6)]):
 cube('Dock_Lamp_Lens',(x,y,z),(.42,.28,.035),'20_Rain_Detail',em);light('Dock_Rain_Lamp_'+str(i),(x,y,z-.05),(x,y,4),260,(.65,.8,1),.55)
light('Gondola_Interior',(0,8,6.05),(0,8,4),90,(1,.63,.3),1.5)
light('Moon_Rim',(25,25,35),(0,5,2),2200,(.25,.42,.7),20)
light('Maldek_Distant_Glow',(0,377,71),(0,365,61),1700,(.55,.73,1),5)
for x in [-7,0,7]:cube('Maldek_Window',(x,378.9,69),(3,.04,2),'19_Cable_Route',em)
# Layered mist: local denser low fog plus sparse long-range haze.
fog=bpy.data.materials['R02_Valley_Fog'];v=next(n for n in fog.node_tree.nodes if n.type=='PRINCIPLED_VOLUME');v.inputs['Density'].default_value=.011;v.inputs['Anisotropy'].default_value=.35
haze=fog.copy();haze.name='R03_Distant_Haze';next(n for n in haze.node_tree.nodes if n.type=='PRINCIPLED_VOLUME').inputs['Density'].default_value=.0018
cube('Distant_Haze',(0,300,60),(500,390,200),'17_Atmosphere',haze)
# Fine wind-slanted rain streaks outside the roofed rooms; visible in practical light.
rain=mat('R03_Rain',(.35,.48,.6),.1,.1);rp=rain.node_tree.nodes.get('Principled BSDF');rp.inputs['Alpha'].default_value=.32
vs=[];fs=[]
for i in range(9000):
 x=rng.uniform(-8,18);y=rng.uniform(0,32);z=rng.uniform(-1,12)
 if -8.2<x<8 and y<7.2 and z<7.6:continue
 p=Vector((x,y,z));length=rng.uniform(.06,.19);a=len(vs);vs.extend([tuple(p),tuple(p+Vector((.007,0,0))),tuple(p+Vector((.035,.025,-length)))]);fs.append((a,a+1,a+2))
meshob('Rain_Streaks_Static_Render_Study',vs,fs,'20_Rain_Detail',rain)
# Keep thick mist down in the valley while reducing haze at the lamp/camera height.
n=fog.node_tree.nodes;l=fog.node_tree.links;geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=-7;r.inputs['From Max'].default_value=6;r.inputs['To Min'].default_value=.023;r.inputs['To Max'].default_value=.0015;l.new(sep.outputs['Z'],r.inputs['Value']);l.new(r.outputs['Result'],v.inputs['Density'])
# Glazed side windows catch rain-light reflections; the boarding aperture stays open.
glass=mat('R03_Wet_Gondola_Glass',(.38,.48,.52),.12);gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=.96;gp.inputs['IOR'].default_value=1.45
n=glass.node_tree.nodes;l=glass.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.28;b.inputs['Distance'].default_value=.002;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],gp.inputs['Normal'])
for loc,size in [((-1.55,8.05,5.475),(.012,4.26,1.15)),((1.55,8.05,5.475),(.012,4.26,1.15)),((0,11.05,5.475),(2.4,.012,1.15))]:
 o=cube('Gondola_Wet_Glass',loc,size,'12_Gondola',glass);world=o.matrix_world.copy();o.parent=bpy.data.objects['Gondola_MOVE_THIS'];o.matrix_world=world
for o in list(col('12_Gondola').objects):
 if o.type=='MESH' and 'Glass' not in o.name:
  mod=o.modifiers.new('Soft_Sheet_Edges','BEVEL');mod.width=.025;mod.segments=3

# Telescope on overlook points toward the remote terminus.
beam('Lookout_Pedestal',(12,5,4),(12,5,5.1),.12,'19_Cable_Route',steel);beam('Lookout_Telescope',(12,4.8,5.15),(11.97,5.65,5.32),.18,'19_Cable_Route',steel)
def camera(n,p,t,lens):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);col('92_Cameras_Lights').objects.link(o);o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=1500;return o
cams=[('platform_rain',camera('CAM_R03_Platform_Rain',(-7,1,4.9),(0,10,5.3),25)),('control_room_night',camera('CAM_R03_Control_Room',(-6.4,-1.9,5.65),(-.4,10,5.1),25)),('relay_terrain',camera('CAM_R03_Relay_Terrain',(67,-35,38),(24,6,2),40)),('cable_route',camera('CAM_R03_Cable_Route',(12,5.7,5.65),(0,220,43),48))]
scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.cycles.transparent_max_bounces=12;scene.render.resolution_x=1400;scene.render.resolution_y=930;scene.view_settings.exposure=-.35
scene['Design revision']='Millford / continuous relay slope, CC0 pines and rainy night 03';scene.camera=cams[0][1]
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.clip_end=1500
for vl in scene.view_layers:
 if vl!=full:
  for name in ['16_Forest','17_Atmosphere','19_Cable_Route','20_Rain_Detail']:
   if name in vl.layer_collection.children:vl.layer_collection.children[name].exclude=True
(OUT/'route_points.json').write_text(json.dumps({'relay_center':[48,13,3],'paths':paths,'maldek_terminal':[0,390,60]},indent=2))
dim=json.loads((BASE/'revision_02/blockout_dimensions.json').read_text());dim['revision']='v2_night_03';dim['relay_center_m']=[48,13,3]
for opening in dim['openings']:
 if opening['name'].startswith('Relay_'):opening['fixed']+=12;opening['center']+=22;opening['base']+=1
(OUT/'blockout_dimensions.json').write_text(json.dumps(dim,indent=2))
notes=bpy.data.texts.get('START_HERE');notes.clear();notes.write('MILLFORD / MALDEK NIGHT STUDY 03\n\nContinuous relay paths and filled eastern shoulder. Relay now at (48,13,3) metres. Textured CC0 Poly Haven pine variants. Cable route to a distant Maldek silhouette. Night lighting, wet surfaces, layered fog and static rain.\n\nFull Shell for rendering; Cutaway and Lower Level for editing. See revision_03/README.md and validation_report.json. No new UE export or engine playtest in this revision. Earlier files preserved.\n')

bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_night_03.blend'));print('R03_SAVED',flush=True)
for name,cam in cams:
 scene.camera=cam;scene.render.filepath=str(OUT/'previews'/f'{name}.png');print('RENDER',name,flush=True);bpy.ops.render.render(write_still=True,layer=full.name)
scene.camera=cams[0][1];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_night_03.blend'));print('R03_COMPLETE',flush=True)

# A separate daylight layout proof makes the filled shoulder and smooth route reviewable.
# Do not save these temporary lighting settings over the night scene.
scene.camera=bpy.data.objects['CAM_R03_Relay_Terrain']
scene.view_settings.exposure=0
for n in scene.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=.4
bpy.data.objects['Overcast_Sun'].data.energy=1.5
for o in bpy.data.collections['17_Atmosphere'].objects:o.hide_render=True
scene.cycles.samples=24;scene.render.resolution_percentage=80
scene.render.filepath=str(OUT/'previews/relay_daylight_layout.png');print('RENDER daylight_layout',flush=True);bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
