import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];SRC=OUT.parent/'passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;s.name='West_Services_Combined';s.frame_set(1)
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
baseline={o.name:[list(row) for row in o.matrix_world] for o in s.objects}
cols={}
for n in ['WS_SHARED_STRUCTURE','WS_SHARED_ROOF','WS_PARCELS_PROXY','WS_RESCUE_PROXY','WS_POWER_PROXY','WS_REVIEW_ONLY']:
 c=bpy.data.collections.new(n);s.collection.children.link(c);cols[n]=c
cur=cols['WS_SHARED_STRUCTURE']
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.76;return m
con=mat('WS_Concrete',(.32,.34,.32));wood=mat('WS_Pine',(.34,.22,.115));green=mat('WS_Petrol',(.055,.17,.15));cream=mat('WS_Cream',(.7,.66,.51));red=mat('WS_Ochre',(.55,.16,.065));steel=mat('WS_Steel',(.18,.21,.22))
def box(n,lo,hi,m=con):
 vs=[(x,y,z) for z in [lo[2],hi[2]] for y in [lo[1],hi[1]] for x in [lo[0],hi[0]]]
 faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
 me=bpy.data.meshes.new('WS_'+n);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new('WS_'+n,me);cur.objects.link(o);me.materials.append(m);return o
def beam(n,a,b,r=.035):
 a=Vector(a);b=Vector(b);v=b-a;u=v.normalized().cross(Vector((0,0,1)))
 if u.length<.01:u=v.normalized().cross(Vector((0,1,0)))
 u.normalize();w=v.normalized().cross(u);vs=[p+r*(math.cos(i*math.tau/8)*u+math.sin(i*math.tau/8)*w) for p in [a,b] for i in range(8)]
 faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 me=bpy.data.meshes.new('WS_'+n);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new('WS_'+n,me);cur.objects.link(o);me.materials.append(green);return o
def rail(n,a,b):
 for h in [.55,1.1]:beam(n+'Rail',Vector(a)+Vector((0,0,h)),Vector(b)+Vector((0,0,h)))
 N=max(1,math.ceil((Vector(b)-Vector(a)).length/1.4))
 for i in range(N+1):
  p=Vector(a).lerp(Vector(b),i/N);beam(n+'Post',p,p+Vector((0,0,1.1)),.04)
def label(n,t,pos,size=.22):
 cu=bpy.data.curves.new(n,'FONT');cu.body=t;cu.size=size;cu.extrude=.001;o=bpy.data.objects.new('WS_'+n,cu);cur.objects.link(o);o.location=pos;o.rotation_euler=(math.pi/2,0,math.pi/2);cu.materials.append(cream)
# Remove exact west boundary rail in this derived copy only. New guard follows level changes.
retired=[]
for o in list(s.objects):
 if o.name.startswith('PL02_Perimeter_0_'):
  retired.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Structural base and upper slab. One owner per floor, roof, party wall.
box('BaseSlab',(-37.45,-5,1),(-31.45,5,1.2))
box('UpperSlab',(-37.45,-5,4.35),(-31.45,5,4.6))
box('BaseEast',(-31.7,-5,1.2),(-31.45,5,4.35))
box('BaseSouth',(-37.2,-5,1.2),(-31.7,-4.75,4.35))
box('BaseNorth',(-37.2,4.75,1.2),(-31.7,5,4.35))
# West wall with independent personnel/removal portal and two ventilation openings.
def wallx(n,x0,x1,y0,y1,z0,z1,holes,m):
 ys=sorted(set([y0,y1]+[v for h in holes for v in h[:2]]));zs=sorted(set([z0,z1]+[v for h in holes for v in h[2:]]))
 for a,b in zip(ys,ys[1:]):
  for c,d in zip(zs,zs[1:]):
   if not any(a>=h[0] and b<=h[1] and c>=h[2] and d<=h[3] for h in holes):box(n,(x0,a,c),(x1,b,d),m)
wallx('BaseWest',-37.45,-37.2,-5,5,1.2,4.35,[(1.4,3,1.2,3.5),(-3.8,-2.3,1.8,2.9),(-.8,.7,2.3,3.4)],con)
# Upper east doors and windows: shell bounds = rough apertures, detail packages inset frames.
wallx('UpperEast',-31.65,-31.45,-5,5,4.6,7.3,[(-3.9,-2.4,4.6,6.95),(1.2,2.9,4.6,6.95),(-1.8,-.4,5.6,6.65),(3.35,4.45,5.6,6.65)],wood)
box('UpperWest',(-37.45,-5,4.6),(-37.25,5,7.3),wood)
box('UpperSouth',(-37.25,-5,4.6),(-31.65,-4.8,7.3),wood)
box('UpperNorth',(-37.25,4.8,4.6),(-31.65,5,7.3),wood)
box('SharedPartyWall',(-37.25,-.1,4.6),(-31.65,.1,7.3),cream)
# Porch and approach; 600 mm rise, four steps and a 1:12 trolley ramp.
box('Porch',(-31.45,-5,4.4),(-29.45,5,4.6),con)
box('RampBottomLanding',(-31.45,-14.2,3.8),(-29.45,-12.2,4),con)
verts=[(x,y,z-d) for d in [0,.18] for x,y,z in [(-31.45,-12.2,4),(-29.45,-12.2,4),(-29.45,-5,4.6),(-31.45,-5,4.6)]]
me=bpy.data.meshes.new('WS_Ramp');me.from_pydata(verts,[],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]);me.update();o=bpy.data.objects.new('WS_TrolleyRamp',me);cur.objects.link(o);me.materials.append(con)
for i in range(4):box('UpperStep',(-31.45,5+i*.3,4),(-29.45,5+(i+1)*.3,4.6-i*.15),con)
box('NorthLanding',(-31.45,6.2,3.8),(-29.45,8.2,4))
# Lower service flight descends west from the north landing.
for i in range(16):box('ServiceStep',(-31.45-(i+1)*.35,6.2,3.65-i*.175),(-31.45-i*.35,8.2,4-(i+1)*.175),con)
box('LowerLanding',(-39.45,6.2,1),(-37.05,8.2,1.2))
box('LowerWalk',(-39.45,1,1),(-37.45,6.2,1.2))
for x in [-37.25,-31.7]:
 for y in [-4.75,4.5]:box('FoundationPier',(x,y,-2.5),(x+.25,y+.25,1),con)
for y,z in [(-13.5,3.8),(-8,4.1),(0,4.4),(7,3.8)]:box('AccessPier',(-31.4,y,-2.5),(-31.15,y+.25,z),con)
# Replacement guards leave the two actual deck entrances open.
rail('OldWestSouth',(-29.45,-15.15,4),(-29.45,-14.2,4))
rail('RampOuter',(-31.45,-12.2,4),(-31.45,-5,4.6));rail('RampInner',(-29.45,-12.2,4),(-29.45,-5,4.6))
rail('RampBottomOuter',(-31.45,-14.2,4),(-31.45,-12.2,4));rail('RampBottomEnd',(-31.45,-14.2,4),(-29.45,-14.2,4))
rail('PorchEdge',(-29.45,-5,4.6),(-29.45,5,4.6));rail('UpperStepOuter',(-29.45,5,4.6),(-29.45,6.2,4))
rail('UpperStepInner',(-31.45,5,4.6),(-31.45,6.2,4))
rail('NorthOuter',(-29.45,8.2,4),(-31.45,8.2,4));rail('NorthShort',(-29.45,7.4,4),(-29.45,8.2,4))
for y in [6.2,8.2]:rail('ServiceStair',(-31.45,y,4),(-37.05,y,1.2))
rail('LowerEnd',(-39.45,8.2,1.2),(-37.05,8.2,1.2));rail('LowerOuter',(-39.45,1,1.2),(-39.45,8.2,1.2));rail('LowerSouth',(-39.45,1,1.2),(-37.45,1,1.2))
# Shared low-pitch roof and porch canopy, independent cutaway collection.
cur=cols['WS_SHARED_ROOF']
for x0,x1,z0,z1 in [(-37.85,-34.45,7.38,8.15),(-34.45,-29.15,8.15,7.38)]:
 o=box('RoofPanel',(x0,-5.45,z0),(x1,5.45,z0+.16),green)
 # slope by vertex position, retaining real thickness
 for v in o.data.vertices:v.co.z+=((v.co.x-x0)/(x1-x0))*(z1-z0)
for y in [-4.9,4.9]:box('PorchPost',(-29.75,y,4.6),(-29.63,y+.12,7.35),wood)
cur=cols['WS_PARCELS_PROXY']
box('ParcelsCounter',(-33.2,-1.9,4.6),(-32.5,-.4,5.5),green)
box('ParcelsShelves',(-37.15,-4.6,4.6),(-36.55,-.4,6.7),wood)
box('ParcelsSecureCabinet',(-35.9,-4.6,4.6),(-34.7,-4.05,6.5),green)
label('ParcelsSign','LUGGAGE / PARCELS',(-31.42,-4.65,7.03),.19)
cur=cols['WS_RESCUE_PROXY']
box('RescueCot',(-35.8,1.4,4.6),(-35.05,3.6,5.25),red)
box('RescueBlankets',(-37.15,.4,4.6),(-36.55,1.6,6.4),cream)
box('RescueHeater',(-34.4,4.45,4.75),(-33.4,4.7,5.3),cream)
label('RescueSign','RESCUE / FIRST AID',(-31.42,.5,7.03),.19)
cur=cols['WS_POWER_PROXY']
box('GeneratorSkid',(-35.8,-2.8,1.2),(-33.3,-1.5,1.42),steel)
box('GeneratorEngine',(-35.6,-2.65,1.42),(-34,-1.65,2.5),green)
box('GeneratorAlternator',(-34,-2.6,1.42),(-33.45,-1.7,2.25),steel)
box('EmergencySwitchboard',(-32.05,1,1.4),(-31.75,2.8,3.1),green)
box('BatteryCabinet',(-34.5,3.9,1.2),(-33.2,4.6,2.2),steel)
for y0,y1,z0,z1 in [(-3.8,-2.3,1.8,2.9),(-.8,.7,2.3,3.4)]:
 for i in range(8):box('Louvre',(-37.48,y0+.05,z0+.05+i*(z1-z0-.1)/8),(-37.32,y1-.05,z0+.09+i*(z1-z0-.1)/8),steel)
beam('ExhaustInterior',(-35.2,-2.2,2.5),(-35.2,-4.85,3.4),.08)
beam('ExhaustRiser',(-35.2,-5.3,2.8),(-35.2,-5.3,8.8),.09)
beam('ExhaustWallConnection',(-35.2,-4.85,3.4),(-35.2,-5.3,3.4),.08)
# Complete shared roof closure and support the access structure on inherited terrain.
cur=cols['WS_SHARED_ROOF']
box('UpperCeiling',(-37.25,-4.8,7.3),(-31.65,4.8,7.38),cream)
def roofz(x):
 return 7.38+(x+37.85)*(.77/3.4) if x<=-34.45 else 8.15-(x+34.45)*(.77/5.3)
for ya,yb in [(-5,-4.8),(4.8,5)]:
 for xa,xb in [(-37.45,-34.45),(-34.45,-31.45)]:
  o=box('Gable',(xa,ya,7.3),(xb,yb,8.2),wood)
  for v in o.data.vertices:
   if v.co.z>8:v.co.z=roofz(v.co.x)
for xa,xb in [(-37.45,-37.25),(-31.65,-31.45)]:
 o=box('AtticSide',(xa,-4.8,7.3),(xb,4.8,8.2),wood)
 for v in o.data.vertices:
  if v.co.z>8:v.co.z=roofz(v.co.x)
cur=cols['WS_SHARED_STRUCTURE']
for x,y,top in [(-39.35,1.1,1),(-39.35,7.85,1),(-37.35,7.85,1),(-37.35,5.9,1)]:box('LowerAccessPier',(x,y,-2.5),(x+.2,y+.2,top),con)
for y in [6.4,8]:beam('ServiceStringer',(-31.6,y,3.62),(-37.05,y,.99),.11)
bpy.context.view_layer.update()
terrain=bpy.data.objects.get('R11_Current_Terrain'); terrain_samples=[]
if terrain:
 inv=terrain.matrix_world.inverted()
 for ob in list(cols['WS_SHARED_STRUCTURE'].objects):
  if ob.type!='MESH' or 'Pier' not in ob.name:continue
  x=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices);y=sum(v.co.y for v in ob.data.vertices)/len(ob.data.vertices)
  ok,pt,n,idx=terrain.ray_cast(inv@Vector((x,y,100)),Vector((0,0,-1)),distance=500)
  if ok:
   ground=(terrain.matrix_world@pt).z;bottom=min(v.co.z for v in ob.data.vertices)
   for v in ob.data.vertices:
    if abs(v.co.z-bottom)<.001:v.co.z=ground-.35
   terrain_samples.append({'pier':ob.name,'ground_z':ground,'toe_z':ground-.35})
(OUT/'terrain_support.json').write_text(json.dumps({'basis':'Inherited R11 Blender terrain, not live Unreal survey','samples':terrain_samples},indent=2))

# Explicit ports reserve future through-wall sleeves; proxy routing does not imply installed engineering.
cur=cols['WS_REVIEW_ONLY']
for n,loc in [('PARCELS_ORIGIN',(-37.45,-5,4.6)),('RESCUE_ORIGIN',(-37.45,0,4.6)),('POWER_ORIGIN',(-37.45,-5,1.2))]:
 o=bpy.data.objects.new('WS_'+n,None);cur.objects.link(o);o.location=loc
manifest={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'scene':s.name,'units':'metres Z up; +Y gondola direction, -X west','retired_context_objects':retired,'preserved_context_transforms':{n:m for n,m in baseline.items() if n not in retired},'collections':{n:[o.name for o in c.objects] for n,c in cols.items()},'upper_floor':4.6,'lower_floor':1.2,'building_bounds_xy':[-37.45,-31.45,-5,5],'status':'Blender blockout; terrain and Unreal integration pending'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Orthographic review cameras, also useful saved views.
for name,pos,target,scale in [('01_Combined',(-61,36,30),(-21,-1,3),49),('02_WestServices',(-51,22,18),(-34,0,4),23),('03_UpperPlan',(-34,0,29),(-34,0,4),23),('04_Arrival',(-25,-18,9),(-33,-1,5),26),('05_LowerEntry',(-43,9,5),(-35,0,2.5),18)]:
 d=bpy.data.cameras.new('WS_'+name);o=bpy.data.objects.new(d.name,d);cur.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
s.camera=bpy.data.objects['WS_01_Combined'];s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.12,.12,.12)
s.render.resolution_x=1500;s.render.resolution_y=1050;s.render.resolution_percentage=100
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
s.render.image_settings.file_format='PNG';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_West_Services_Blockout.blend'))
(OUT/'previews').mkdir(exist_ok=True)
for name in ['01_Combined','02_WestServices','03_UpperPlan','04_Arrival','05_LowerEntry']:
 s.camera=bpy.data.objects['WS_'+name];cols['WS_SHARED_ROOF'].hide_render=name=='03_UpperPlan'
 s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('BUILD COMPLETE',flush=True)

