"""Non-destructive revision: run in background with revision 01 loaded; save to revision_02.
Procedural terrain/foliage and fitted steel study are original geometry. PBR textures: Poly Haven CC0.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, Matrix, noise
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'revision_02'; ASSETS=OUT/'assets'
scene=bpy.context.scene
for lc in bpy.context.view_layer.layer_collection.children: lc.exclude=False
bpy.context.view_layer.update()
COLS={c.name:c for c in scene.collection.children}
def col(name):
    if name not in COLS:
        c=bpy.data.collections.new(name);scene.collection.children.link(c);COLS[name]=c
    return COLS[name]
for n in ['15_Terrain','16_Forest','17_Atmosphere','18_Cliff_Anchors']:col(n)
def remove(o):
    if o: bpy.data.objects.remove(o,do_unlink=True)
def put(o,name,collection,mat,collision=False,export=True):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    col(collection).objects.link(o)
    if mat:o.data.materials.clear();o.data.materials.append(mat);o.color=mat.diffuse_color
    o['collision']=collision;o['export_geometry']=export
    return o
def cube(name,loc,size,collection,mat,collision=False,export=True):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return put(o,name,collection,mat,collision,export)
def beam(name,a,b,thick,collection,mat,collision=False):
    a,b=Vector(a),Vector(b);w,h=thick if isinstance(thick,tuple) else (thick,thick)
    o=cube(name,(a+b)/2,(w,h,(b-a).length),collection,mat,collision);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def basic(name,color,metal=0,rough=.7):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);return m,p
anchor=bpy.data.objects.new('Texture_World_Metres',None);col('90_References').objects.link(anchor)
def textured(name,asset,tint,metal=.0):
    m,p=basic(name,tint,metal);n=m.node_tree.nodes;l=m.node_tree.links
    coord=n.new('ShaderNodeTexCoord');coord.object=anchor
    scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.5;l.new(coord.outputs['Object'],scale.inputs[0])
    channels={}
    for suffix in ['diff','rough','disp']:
        f=next(ASSETS.glob(f'{asset}_{suffix}_1k.*'));im=bpy.data.images.load(str(f),check_existing=True);im.pack()
        if suffix!='diff':im.colorspace_settings.name='Non-Color'
        t=n.new('ShaderNodeTexImage');t.image=im;t.projection='BOX';t.projection_blend=.2;l.new(scale.outputs['Vector'],t.inputs['Vector']);channels[suffix]=t
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.58;mix.inputs[2].default_value=(*tint,1);l.new(channels['diff'].outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
    l.new(channels['rough'].outputs[0],p.inputs['Roughness'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.65;bump.inputs['Distance'].default_value=.035 if metal==0 else .009;l.new(channels['disp'].outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m
concrete=textured('R02_Weathered_Concrete','concrete_floor',(.48,.51,.49))
steel=textured('R02_Chipped_Painted_Steel','rusty_painted_metal',(.16,.20,.19),.65)
red=textured('R02_Oxide_Red_Sheet_Steel','rusty_painted_metal',(.55,.13,.075),.55)
zinc,zp=basic('R02_Galvanized_Grating',(.25,.31,.29),.82,.44)
wood,wp=basic('R02_Damp_Timber',(.11,.07,.035),0,.85)
yellow,yp=basic('R02_Worn_Safety_Paint',(.55,.30,.045),.25,.65)
# Assign the same material family throughout the structure.
for o in list(scene.objects):
    if o.type!='MESH' or not o.data.materials:continue
    old=o.data.materials[0].name
    replacement={'Concrete_Warm':concrete,'Concrete_Service':concrete,'Deck':concrete,'Steel':steel,'Timber':wood,'Gondola_Red':red,'Safety_Amber':yellow}.get(old)
    if replacement:o.data.materials.clear();o.data.materials.append(replacement);o.color=replacement.diffuse_color
# Remove the display plinth and floating scene labels, but preserve the revision-01 file.
remove(bpy.data.objects.get('Site_Presentation_Plinth'))
for o in list(col('91_Labels').objects):o.hide_render=True;o.hide_set(True)
for o in list(col('90_References').objects)+list(col('93_Upper_Scale_References').objects):
    if o.name.startswith(('Operator','Platform_Person','SM_Scale')):o.hide_render=True;o.hide_set(True)
# Grating is real open geometry, with a simple invisible collision plate per module.
class Bars:
    def __init__(self):self.v=[];self.f=[]
    def box(self,x,y,z,w,d,h):
        k=len(self.v)
        self.v += [(x+sx*w/2,y+sy*d/2,z+sz*h/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.f += [tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    def finish(self,name,collection,material):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.v,[],self.f);mesh.update();o=bpy.data.objects.new(name,mesh);col(collection).objects.link(o);return put(o,name,collection,material)
def grating(name,x0,x1,y0,y1,z,collection,spacing=.10):
    b=Bars();w=x1-x0;d=y1-y0
    for i in range(math.ceil(w/spacing)+1):
        x=x0+w*i/math.ceil(w/spacing);b.box(x,(y0+y1)/2,z-.025,.016,d,.05)
    for i in range(math.ceil(d/.35)+1):
        y=y0+d*i/math.ceil(d/.35);b.box((x0+x1)/2,y,z-.017,w,.014,.025)
    for x in [x0,x1]:b.box(x,(y0+y1)/2,z-.045,.045,d,.09)
    for y in [y0,y1]:b.box((x0+x1)/2,y,z-.045,w,.045,.09)
    result=b.finish(name,collection,zinc)
    proxy=cube(name+'_Collision',((x0+x1)/2,(y0+y1)/2,z-.045),(w,d,.09),collection,zinc,True,False);proxy.hide_render=True;proxy.hide_set(True);proxy['collision_only']=True
    return result
# Replace every solid stair tread with open bar grating and steel stringers. Retain rise/run.
dim=json.loads((BASE/'blockout_dimensions.json').read_text())
for st in dim['stairs']:
    collection='10_Parking_and_Arrival' if st['name']=='Arrival' else '06_Stairs_and_Landings'
    for o in list(col(collection).objects):
        if o.name.startswith(st['name']+'_Tread_'):
            top=o.location.z+o.dimensions.z/2;cx,cy=o.location.x,o.location.y;w,d=o.dimensions.x,o.dimensions.y;name=o.name
            remove(o);grating(name+'_Open',cx-w/2,cx+w/2,cy-d/2,cy+d/2,top,collection,.085)
    for side in [-1,1]:
        x=st['x']+side*(st['width']/2+.06)
        beam(st['name']+'_Channel_Stringer',(x,st['y0'],st['z0']-.17),(x,st['y1'],st['z1']-.17),(.065,.24),collection,steel)
        # Foot plates visibly bolt the flight to its landing.
        cube(st['name']+'_Footplate',(x,st['y0'],st['z0']+.025),(.26,.32,.05),collection,steel)
# Make small service landings from the same grating modules.
for name in ['Internal_Lower_Landing','Internal_Stair_Top','Exterior_Lower_Landing','Exterior_Upper_Landing','Overlook_Bridge','Overlook_North_Link']:
    o=bpy.data.objects.get(name)
    if not o:continue
    x,y,z=o.location;w,d,h=o.dimensions;cn=o.users_collection[0].name;remove(o);grating(name+'_Steel',x-w/2,x+w/2,y-d/2,y+d/2,z+h/2,cn)
# Open the drive gallery to the cliff on north/east. Retain the generator-side enclosure.
for o in list(col('04_Lower_Drive').objects):
    if o.name.startswith(('Drive_North','Drive_East')):remove(o)
    elif o.name.startswith('Drive_West'):
        o.dimensions.z=.9;o.location.z=.45;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
gr = grating('Open_Drive_Apron',-2,6,7,11.5,0,'04_Lower_Drive')
# Simple railing lengths with clear approach openings.
def railing(name,a,b,z,collection):
    a,b=Vector((*a,z)),Vector((*b,z));d=b-a
    for h in [.55,1.1]:beam(name+'_Rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.045,collection,steel)
    count=max(1,math.ceil(d.length/1.4))
    for i in range(count+1):
        p=a+d*i/count;beam(name+'_Post',p,p+Vector((0,0,1.1)),.055,collection,steel)
    guard=cube(name+'_Guard',(a+b)/2+Vector((0,0,.55)),(.08,d.length,1.1),collection,steel,True,False)
    guard.rotation_euler[2]=-math.atan2(d.x,d.y);guard.hide_render=True;guard.hide_set(True);guard['collision_only']=True
railing('Drive_Cliff_Edge',(-2,11.5),(6,11.5),0,'04_Lower_Drive')
railing('Drive_East_Exposure',(6,1.7),(6,11.5),0,'04_Lower_Drive')
railing('Drive_West_Apron',(-2,7),(-2,11.5),0,'04_Lower_Drive')
# Upper dock extends toward the valley; a 6 m car now has an elongated silhouette.
gr = grating('Dock_Extension_West',-4,-1.8,7,11.5,4,'01_Upper_Platform')
gr = grating('Dock_Extension_East',1.8,3.6,8.4,11.5,4,'01_Upper_Platform')
railing('Dock_Extension_West_Edge',(-4,7),(-4,11.5),4,'01_Upper_Platform')
railing('Dock_Extension_East_Edge',(3.6,8.4),(3.6,11.5),4,'01_Upper_Platform')
railing('Dock_Extension_West_End',(-4,11.5),(-1.8,11.5),4,'01_Upper_Platform')
railing('Dock_Extension_East_End',(1.8,11.5),(3.6,11.5),4,'01_Upper_Platform')
root=bpy.data.objects['Gondola_MOVE_THIS'];parts=[o for o in scene.objects if o.parent==root]
for o in parts:
    world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
    if o.type=='MESH':
        o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
        for v in o.data.vertices:v.co.y=5.05+(v.co.y-5.05)*(6/3.8)
root.location=(0,8.05,4);bpy.context.view_layer.update()
for o in parts:
    o.parent=root;o.matrix_world=Matrix.Identity(4)
# External rub strips and slim mullions reinforce sheet construction on the long car.
for x in [-1.59,1.59]:
    for z in [4.15,4.85,6.28]:
        o=beam('Gondola_Rub_Strip',(x,5.05,z),(x,11.05,z),.055,'12_Gondola',steel);world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
    for y in [6.7,8.4,10.1]:
        o=beam('Gondola_Window_Mullion',(x,y,4.9),(x,y,6.05),.04,'12_Gondola',steel);world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
# Flywheel becomes a visible rim/spoke mechanism in the exposed work area.
fly=bpy.data.objects.get('Drive_Flywheel');remove(fly)
for o in list(col('04_Lower_Drive').objects):
    if o.name.startswith('Drive_Motor'):o.location.y+=2.2
bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=8,location=(2.1,6.7,1.05),major_radius=.86,minor_radius=.09,rotation=(math.pi/2,0,0))
put(bpy.context.object,'Exposed_Flywheel_Rim','04_Lower_Drive',steel)
for i in range(8):
    a=2*math.pi*i/8;beam('Flywheel_Spoke',(2.1,6.7,1.05),(2.1+.83*math.cos(a),6.7,1.05+.83*math.sin(a)),.065,'04_Lower_Drive',steel)
beam('Flywheel_Axle',(2.1,6.15,1.05),(2.1,7.1,1.05),.14,'04_Lower_Drive',steel)
# Exposed structure below the concrete: load-bearing members read as a cantilever into the cliff.
for x in [-1.7,5.7]:
    beam('Dock_Primary_Girder',(x,0,3.5),(x,11.5,3.5),(.20,.38),'18_Cliff_Anchors',steel)
    beam('Drive_Apron_Girder',(x,0,-.3),(x,11.5,-.3),(.18,.32),'18_Cliff_Anchors',steel)
    beam('Cliff_Knee_Brace',(x,.2,-3.5),(x,10,-.4),(.18,.20),'18_Cliff_Anchors',steel)
    for y in [1,7,10.5]:beam('Open_Gallery_Post',(x,y,-.35),(x,y,3.5),(.16,.16),'18_Cliff_Anchors',steel)
    cube('Anchor_Block',(x,.1,-2.5),(.9,1.0,3.0),'18_Cliff_Anchors',concrete,True)
for y in [1,5,8.2,11.2]:beam('Dock_Crossbeam',(-4,y,3.56),(6,y,3.56),(.15,.25),'18_Cliff_Anchors',steel)
# Terrain: a sculptable height mesh with a steep northern gorge, western hill and eastern relay spur.
paths=[[(14,-6,0),(18.5,-7,0),(21,-6,.4),(26,-4,1),(26,-1,2)],[(26,3,2),(26,10,3),(19,11,4),(15,5,4)], [(-13,-15,-1),(-11.5,-15,0)]]
for st in dim['stairs']:paths.append([(st['x'],st['y0'],st['z0']),(st['x'],st['y1'],st['z1'])])
pads=[(-15,-8,-6,0,3.60),(-8,-3,-4,0,3.60),(-2,6,-6,0,-.34),(8,15,-6,0,-.34),(24,28,-1,3,1.66),(-21,-13,-18,-12,-1.34)]
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def nearest(x,y,points):
    best=(1e9,0)
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
        dist=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
        if dist<best[0]:best=(dist,a[2]+t*(b[2]-a[2]))
    return best
def height(x,y):
    n=noise.noise(Vector((x*.055,y*.055,1.7)))
    detail=noise.noise(Vector((x*.28,y*.28,2.4)))
    west=4*(1-smooth(-18,-6,x));east=2*smooth(16,28,x)
    gorge=(1-smooth(13,26,abs(x-1)))*smooth(2,12,y+1.4*n)
    h=-.5+west+east+2.7*n+.65*detail-24*gorge+max(0,y-32)*.14
    # Sculpt level pads for the grounded rooms, with a soft cut into surrounding hills.
    for x0,x1,y0,y1,z in pads:
        dist=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1));weight=1-smooth(0,3,dist)
        h=h*(1-weight)+z*weight
    # Ground the footpaths while leaving the drive apron genuinely over the drop.
    for path in paths:
        dist,z=nearest(x,y,path);weight=1-smooth(.8,2.7,dist)
        # Below stairs, grade gently beneath the stringers rather than fill the flight.
        target=z-.38;h=h*(1-weight)+target*weight
    # Drive floor stays at grade at its sheltered south end and peels away toward the valley.
    if -2<=x<=6 and 0<=y<=2:h=min(h,-.34)
    return h
v=[];f=[];nx=181;ny=181;step=1.0;ox=-75;oy=-65
for j in range(ny):
    for i in range(nx):
        x=ox+i*step;y=oy+j*step;v.append((x,y,height(x,y)))
for j in range(ny-1):
    for i in range(nx-1):
        a=j*nx+i;f.append((a,a+1,a+nx+1,a+nx))
mesh=bpy.data.meshes.new('Sculptable_Cliff_Grid');mesh.from_pydata(v,[],f);mesh.update()
terrain=bpy.data.objects.new('Terrain_Cliff_And_Relay_Spur',mesh);col('15_Terrain').objects.link(terrain);terrain['export_geometry']=False;terrain['collision']=False;terrain['note']='Sculptable 1 m grid. Stage terrain separately as a UE Landscape or terrain mesh; do not use one convex hull.'
rock,rp=basic('R02_Cliff_Rock_and_Forest_Soil',(.20,.24,.20));n=rock.node_tree.nodes;l=rock.node_tree.links
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.50;ramp.color_ramp.elements[0].color=(.13,.16,.17,1);ramp.color_ramp.elements[1].position=.94;ramp.color_ramp.elements[1].color=(.095,.14,.08,1);l.new(sep.outputs['Z'],ramp.inputs[0])
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.2;tex.inputs['Detail'].default_value=5;l.new(geo.outputs['Position'],tex.inputs['Vector'])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.45;l.new(ramp.outputs[0],mix.inputs[1]);l.new(tex.outputs['Fac'],mix.inputs[2]);l.new(mix.outputs[0],rp.inputs['Base Color'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.65;bump.inputs['Distance'].default_value=.23;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],rp.inputs['Normal']);terrain.data.materials.append(rock)
for p in terrain.data.polygons:p.use_smooth=True
# Compact retaining/footing geometry joins relay pad and public hill to the sculpted ground.
for x,y,z,w,d in [(26,1,2,4.25,4.25),(-11.5,-3,4,7.2,6.2),(-5.5,-2,4,5.2,4.2)]:
    base=height(x,y)-.22;cube('Bedrock_Pad',(x,y,(base+z-.3)/2),(w,d,max(.16,z-.3-base)),'18_Cliff_Anchors',concrete)
# Extend any remaining support feet into their actual local ground surface.
for o in list(col('14_Site_Structure').objects):
    if o.type=='MESH':
        top=o.location.z+o.dimensions.z/2;bottom=min(top-.2,height(o.location.x,o.location.y)-.4)
        o.dimensions.z=top-bottom;o.location.z=(top+bottom)/2
# Thin gravel paths meet the terrain bed; they no longer float between solid blocks.
gravel,gp=basic('R02_Damp_Path_Gravel',(.15,.17,.13),0,.95)
for o in col('09_Relay_and_Paths').objects:
    if o.name.startswith(('Fuel_To_Relay','Relay_To_Overlook')):
        o.data.materials.clear();o.data.materials.append(gravel)
# Forest study: deterministic linked conifer meshes, not downloadable production trees.
bark,bp=basic('R02_Pine_Bark',(.07,.045,.025));needles,np=basic('R02_Pine_Needles',(.025,.070,.043));np.inputs['Roughness'].default_value=.9
rng=random.Random(127)
def conifer_mesh(seed):
    r=random.Random(seed);vs=[];fs=[];mids=[]
    def tapered(a,b,r0,r1,sides=7,material=0):
        a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');base=len(vs)
        for p,rr in [(a,r0),(b,r1)]:
            for k in range(sides):vs.append(tuple(p+q@Vector((rr*math.cos(2*math.pi*k/sides),rr*math.sin(2*math.pi*k/sides),0))))
        for k in range(sides):fs.append((base+k,base+(k+1)%sides,base+sides+(k+1)%sides,base+sides+k));mids.append(material)
        fs.append(tuple(base+k for k in reversed(range(sides))));mids.append(material)
        fs.append(tuple(base+sides+k for k in range(sides)));mids.append(material)
    tapered((0,0,0),(0,0,12),.22,.025,9)
    for tier in range(13):
        z=2+tier*.70;radius=(12-z)*.27
        for branch in range(7):
            a=branch*2*math.pi/7+tier*.67+r.uniform(-.2,.2);length=radius*r.uniform(.7,1.18)
            end=(math.cos(a)*length,math.sin(a)*length,z-r.uniform(.15,.55));tapered((0,0,z),end,.036,.007,5)
            # Irregular tapered needle clusters distributed along each bough.
            for t in [.25,.50,.75,1.0]:
                p=Vector((end[0]*t,end[1]*t,z+(end[2]-z)*t));spread=(1-t*.5)*radius*.22
                tapered(p-Vector((0,0,.20)),p+Vector((.1*math.cos(a),.1*math.sin(a),.65+r.random()*.3)),spread,.01,6,1)
    tapered((0,0,10.4),(0,0,12.6),.45,.01,7,1)
    me=bpy.data.meshes.new('Pine_Prototype_'+str(seed));me.from_pydata(vs,[],fs);me.materials.append(bark);me.materials.append(needles)
    for p,mi in zip(me.polygons,mids):p.material_index=mi
    return me
prototypes=[conifer_mesh(i+50) for i in range(4)]
count=0
for attempt in range(1600):
    if count>=250:break
    x=rng.uniform(-62,72);y=rng.uniform(-48,72)
    # Keep the working compound, station sightline and all routes clear.
    if -23<x<19 and -21<y<14:continue
    if 22<x<30 and -3<y<5:continue
    if 13<x<40 and 12<y<42:continue
    if any(nearest(x,y,path)[0]<2.3 for path in paths):continue
    z=height(x,y)
    if y>4 and -7<x<12:continue
    me=prototypes[count%len(prototypes)];o=bpy.data.objects.new(f'Forest_Pine_{count:03}',me);col('16_Forest').objects.link(o)
    o.location=(x,y,z-.12);s=rng.uniform(.65,1.45);o.scale=(s,s,s*rng.uniform(.9,1.2));o.rotation_euler[2]=rng.random()*math.tau;o['export_geometry']=False;o['collision']=False;count+=1
# Atmospheric lighting, practical warm windows, and low valley fog.
world=scene.world;world.use_nodes=True;world.node_tree.nodes.clear();wn=world.node_tree.nodes;wl=world.node_tree.links
bg=wn.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.29,.40,.49,1);bg.inputs['Strength'].default_value=.42;wo=wn.new('ShaderNodeOutputWorld');wl.new(bg.outputs[0],wo.inputs['Surface'])
def light(name,loc,energy,color,size=5,kind='AREA',target=None):
    data=bpy.data.lights.new(name,kind);data.energy=energy;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);col('92_Cameras_Lights').objects.link(o);o.location=loc
    if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o
sun=light('Overcast_Sun',(20,20,45),2.0,(.72,.82,1),kind='SUN',target=(0,0,0));sun.data.angle=.4
light('Sky_Fill',(0,20,28),17000,(.57,.73,1),25,target=(0,0,0))
light('Cliff_Bounce',(15,25,3),2500,(.58,.72,.76),18,target=(0,3,1))
light('Control_Warmth',(-6,-2,6.75),250,(1,.59,.25),2,target=(-6,1,4.5))
light('Hall_Warmth',(-12,-3,6.8),340,(1,.60,.27),3,target=(-12,1,4))
light('Drive_Work_Lamp',(3,4.5,3.1),180,(1,.65,.30),1.3,target=(2,7,0))
light('Relay_Warmth',(26,1,4.5),100,(1,.57,.24),1.2,target=(26,-1,2))
# Physical lamp housings help the lighting read as station infrastructure.
for x,y,z in [(-5.0,1.0,6.8),(4.8,5.0,6.8),(3,4.5,3.15)]:cube('Industrial_Lamp_Housing',(x,y,z),(.5,.23,.12),'01_Upper_Platform',steel)
fog=bpy.data.materials.new('R02_Valley_Fog');fog.use_nodes=True;fog.node_tree.nodes.clear();fn=fog.node_tree.nodes;fl=fog.node_tree.links
volume=fn.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.58,.69,.72,1);volume.inputs['Density'].default_value=.004;volume.inputs['Anisotropy'].default_value=.2
fo=fn.new('ShaderNodeOutputMaterial');fl.new(volume.outputs['Volume'],fo.inputs['Volume'])
cube('Valley_Fog_Volume',(0,27,-10),(145,135,37),'17_Atmosphere',fog,False,False)
# Landscape cameras see the actual model and environment, not generated concept imagery.
def camera(name,loc,target,lens=38):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);col('92_Cameras_Lights').objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=500;return o
hero=camera('CAM_R02_Cliff_Exterior',(37,43,24),(2,1,1),35)
service=camera('CAM_R02_Exposed_Drive_Eye',(4.7,8.7,1.65),(0,10.7,3.8),22)
site=camera('CAM_R02_Terrain_and_Relay',(49,-48,34),(4,0,1),35)
scene['Design revision']='Millford V2 / cliff and steel study 02'
scene['Status']='Cliff terrain, open drive gallery, steel grating and longer gondola. UE5 playtest pending.'
scene['Gondola dimensions']='3.1 m wide x 6.0 m long; entry remains at Y=5.05 m.'
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.device='CPU'
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
# Use full shell for the atmospheric views. Preserve the cutaway and lower layers for editing.
full=scene.view_layers['02_Full_Shell'];bpy.context.window.view_layer=full
for vl in scene.view_layers:
    vl.use=(vl==full)
    if vl.name!='02_Full_Shell':
        for name in ['16_Forest','17_Atmosphere']:
            if name in vl.layer_collection.children:vl.layer_collection.children[name].exclude=True
# Hide non-player reference figures for renders except the mechanic, now on the open gallery.
for o in col('90_References').objects:
    if o.name.startswith('Service_Person'):o.location.y+=9.5
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.clip_end=500
            sp.region_3d.view_distance=65;sp.region_3d.view_location=(2,1,1);sp.region_3d.view_rotation=hero.rotation_euler.to_quaternion();sp.region_3d.view_perspective='PERSP'
scene.camera=hero
notes=bpy.data.texts.get('START_HERE');notes.clear();notes.write('MILLFORD CLIFF STUDY 02\n\nRevision 01 is preserved. This file adds a sculptable cliff mesh, grounded relay spur and footpaths, exposed drive apron, steel grating stair flights, a 6 m sheet-steel gondola and shared weathered materials.\n\nView layers: Full Shell for context; Cutaway / Lower Level hide the forest and fog for editing.\nTerrain is in collection 15; forest is linked study geometry in 16; fog is in 17.\nPoly Haven CC0 textures are packed into this blend. Marketplace meshes were researched but not downloaded. See ASSET_RESEARCH.md.\nTerrain and trees are not production UE assets. Import and movement checks remain pending.\n')
dim['revision']='v2_cliff_02';dim['gondola_length_m']=6.0;dim['gondola_pivot_m']=[0,8.05,4];dim['drive_apron_north_y_m']=11.5
(OUT/'blockout_dimensions.json').write_text(json.dumps(dim,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_cliff_02.blend'))
print('REVISION_02_SAVED',count,'trees',len(scene.objects),'objects',flush=True)
for name,cam in [('cliff_exterior',hero),('exposed_drive',service),('terrain_and_relay',site)]:
    scene.camera=cam;scene.render.filepath=str(OUT/'previews'/f'{name}.png');print('RENDER_START',name,flush=True);bpy.ops.render.render(write_still=True,layer=full.name)
scene.camera=hero;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_cliff_02.blend'));print('REVISION_02_COMPLETE',flush=True)
