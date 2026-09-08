"""Separate concept study: geared drive, tilted bullwheel and return tension carriage.
Metres. Retains installed rope separation; no Unreal replacement/export performed.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
def material(name,color,metal=.35):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.78
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=4
 position=n.new('ShaderNodeNewGeometry');l.new(position.outputs['Position'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.27;ramp.color_ramp.elements[0].color=(*[c*.6 for c in color],1);ramp.color_ramp.elements[1].position=.7;ramp.color_ramp.elements[1].color=(*color,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.018;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m
paint=material('Aged grey green paint',(.24,.31,.265));steel=material('Graphite cast iron',(.065,.08,.085));zinc=material('Dull machined steel',(.36,.38,.36),.7);rust=material('Oxidized joints',(.22,.095,.035));amber=material('Faded ochre guards',(.55,.31,.08));rubber=material('Rope and liner',(.024,.03,.032),0);concrete=material('Concrete',(.26,.28,.27),0);ivory=material('Lettering',(.8,.82,.73),0)
def box(name,p,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('Cast edge bevel','BEVEL');b.width=.025;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def rod(name,a,b,r,m):
 a=Vector(a);b=Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def line(name,pts,r,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;c.use_fill_caps=True;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(m);return o
def label(text,p,size=.24):
 c=bpy.data.curves.new(text,'FONT');c.body=text;c.size=size;c.extrude=.001;o=bpy.data.objects.new(text,c);bpy.context.collection.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,0);c.materials.append(ivory);return o
def bolts(p,sx,sy):
 for x in [-sx,sx]:
  for y in [-sy,sy]:rod('Anchor stud',(p[0]+x,p[1]+y,p[2]),(p[0]+x,p[1]+y,p[2]+.10),.047,zinc)
D=Vector((-2.35,0,2.955));u=-D.normalized();v=Vector((0,-1,0));n=u.cross(v).normalized();R=D.length/2
def wheel(origin,name):
 C=Vector(origin)
 for off in [-.12,.12]:line(name+' rim',[C+n*off+(u*math.cos(t)+v*math.sin(t))*(R-.06) for t in [i*math.tau/128 for i in range(129)]],.075,zinc)
 line(name+' replaceable groove liner',[C+(u*math.cos(t)+v*math.sin(t))*(R-.035) for t in [i*math.tau/128 for i in range(129)]],.055,rubber)
 for i in range(12):
  t=i*math.tau/12;rod(name+' tapered spoke',C+(u*math.cos(t)+v*math.sin(t))*.30,C+(u*math.cos(t)+v*math.sin(t))*(R-.15),.095,paint)
 rod(name+' hub',C-n*.28,C+n*.28,.35,steel)
 for i in range(8):
  t=i*math.tau/8;q=C+n*.3+(u*math.cos(t)+v*math.sin(t))*.24;rod(name+' hub bolt',q,q+n*.065,.035,zinc)
 # Exact tangential joins to a half-wrap. Incoming cabin stops before this bend.
 line(name+' continuous rope',[C+u*R-v*7,C+u*R]+[C+u*R*math.cos(t)+v*R*math.sin(t) for t in [i*math.pi/96 for i in range(97)]]+[C-u*R-v*7],.032,rubber)
 return C
C=wheel((-1.175,0,8.0),'DRIVE')
# Both independent shaft bearings sit outside the rotating wheel envelope.
for side in [-1,1]:
 q=C+n*side*.52;rod('Independent bullwheel bearing',q-n*.16,q+n*.16,.43,steel)
 f=Vector((-4.0 if side>0 else 2.2,0,9.8));rod('Bearing load strut',q,f,.18,paint)
for x in [-4,2.2]:
 rod('Portal column',(x,0,.4),(x,0,10),.27,paint);box('Foundation',(x,0,.0),(1.8,1.8,.6),concrete);box('Base plate',(x,0,.36),(.95,.95,.12),rust);bolts((x,0,.42),.34,.34)
rod('Portal crosshead',(-4,0,9.8),(2.2,0,9.8),.28,paint)
# Lower equipment drives a guarded vertical shaft; upper bevel gearbox turns onto tilted wheel axis.
G=C+n*1.35;rod('Bullwheel output shaft',C+n*.32,G,.16,zinc)
box('Upper angle gearbox',G,(.9,.85,.85),paint)
low=Vector((G.x,G.y,1.15));rod('Vertical drive shaft',low,G,.10,zinc)
for z in [2.4,4.6,6.6]:
 rod('Shaft steady bearing',(G.x,G.y,z-.14),(G.x,G.y,z+.14),.22,steel)
 rod('Bearing frame tie',(G.x,G.y,z),(-4,0,z),.09,paint)
# Open front guard bars reveal shaft without presenting an unguarded operating model.
for dx in [-.32,.32]:rod('Shaft cage upright',(G.x+dx,-.32,1.5),(G.x+dx,-.32,G.z-.45),.035,amber)
for z in [1.6+i*.3 for i in range(18)]:rod('Shaft cage crossbar',(G.x-.32,-.32,z),(G.x+.32,-.32,z),.014,amber)
box('Lower reducer',low,(1.0,.85,.9),paint);box('Drive concrete bed',(G.x+1.1,0,.1),(4.4,2.4,.45),concrete)
motor=low+Vector((2.25,0,0));rod('Finned electric motor',motor-Vector((.65,0,0)),motor+Vector((.65,0,0)),.42,paint)
for i in range(13):
 x=motor.x-.6+i*.1;rod('Cooling fin',(x-.018,0,1.15),(x+.018,0,1.15),.46,steel)
box('Motor terminal box',(motor.x,0,1.7),(.5,.45,.25),paint)
rod('Input shaft',low+Vector((.4,0,0)),motor-Vector((.65,0,0)),.09,zinc)
brake=low+Vector((.85,0,0));rod('SERVICE BRAKE disc',brake-Vector((.035,0,0)),brake+Vector((.035,0,0)),.36,zinc)
box('Service brake spring caliper',brake+Vector((0,-.30,0)),(.26,.28,.4),amber)
for x in [motor.x-.45,motor.x+.45]:box('Motor saddle',(x,0,.55),(.22,1.15,.3),steel)
# Safety disc rigidly fixed to the bullwheel, independent of gear train failure.
line('Bullwheel SAFETY BRAKE disc',[C-n*.24+(u*math.cos(t)+v*math.sin(t))*(R-.25) for t in [i*math.tau/128 for i in range(129)]],.085,zinc)
for k in [-.65,.65]:
 q=C-n*.24+(u*math.cos(k)+v*math.sin(k))*(R-.25)
 box('Spring applied safety caliper',q,(.32,.42,.42),amber);rod('Safety brake torque reaction',q,Vector((2.2,0,9.0+k)),.10,steel)
label('01  MILLFORD / GEARED DRIVE',(-4.6,-1.4,-.55),.29)
label('MOTOR > SERVICE BRAKE > REDUCER',(-4.6,-1.4,-1.0),.18)
label('GUARDED SHAFT > ANGLE GEAR > BULLWHEEL',(-4.6,-1.4,-1.32),.18)
# Separate return station inset: translating bearing carriage, hydraulic cylinder, no second main motor.
T=wheel((10.0,0,5.0),'RETURN')
rod('Continuous return axle',T-n*.75,T+n*.75,.16,zinc)
for side in [-1,1]:
 q=T+n*side*.52;rod('Return shaft bearing',q-n*.16,q+n*.16,.4,steel);foot=Vector((8.0 if side>0 else 12,0,2.5));rod('Carriage bearing pedestal',foot,q,.20,paint)
for x in [8,12]:
 box('Tension rail',(x,.2,2.1),(.25,4.5,.25),zinc);box('Sliding carriage runner',(x,0,2.4),(.6,1.4,.3),paint)
 for y in [-1.9,2.2]:rod('Return frame leg',(x,y,0),(x,y,2.0),.22,steel)
rod('Carriage crossbeam',(8,0,2.4),(12,0,2.4),.19,paint)
rod('Hydraulic tension cylinder',(10,2.7,2.4),(10,1.0,2.4),.18,amber);rod('Tension piston',(10,1.0,2.4),(10,0,2.4),.09,zinc)
rod('Fixed hydraulic reaction beam',(8,2.7,2.4),(12,2.7,2.4),.18,steel)
for x in [8,12]:box('Return foundation',(x,.2,-.2),(1.2,5.2,.4),concrete)
box('Hydraulic power pack',(12.9,1.7,.6),(.75,.85,1.2),paint)
line('Hydraulic hose',[(12.6,1.7,1.0),(11.8,2.9,1.0),(10,2.9,2.4),(10,2.5,2.55)],.025,rubber)
label('02  MALDEK / RETURN + TENSION',(7,-3.5,-.7),.27)
label('FREE WHEEL / SLIDING BEARINGS / HYDRAULICS',(7,-3.5,-1.1),.18)
box('Studio floor',(4,0,-1.8),(200,200,.2),material('Background',(.035,.045,.052),0))
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.12,.16,.2,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
for name,p,power,size in [('Key',(1,-8,16),3500,10),('Rim',(2,8,14),4200,8),('Fill',(14,-2,10),1800,8)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector((4,0,4))-o.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(19,-29,18);cam.rotation_euler=(Vector((4,0,4))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=25
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Terminal_Drive_Study.blend'));bpy.ops.render.render(write_still=True)
cam.location=(-8,-13,11);cam.rotation_euler=(Vector((-1.5,0,7.4))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=8.8;scene.render.filepath=str(OUT/'drive_detail.png');bpy.ops.render.render(write_still=True)
(OUT/'verification.json').write_text(json.dumps({'rope_diameter_m':.064,'bullwheel_pitch_diameter_m':2*R,'wheel_rpm_at_3_5_m_s':3.5/R*60/math.tau,'nominal_motor_rpm':1500,'illustrative_total_ratio':1500/(3.5/R*60/math.tau),'wrap_degrees':180,'single_cabin_reverses_before_wheel':True,'unreal_imported':False,'geometry_objects':len(bpy.data.objects),'limits':'Layout study only. Gear/bearing/brake sizing, traction margin, hydraulic stroke and exact station retrofit require further validation.'},indent=2))
