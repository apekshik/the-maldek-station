"""Build an editable, metre-scale Millford blockout in a NEW background Blender process.
Run: Blender --background --factory-startup --python art/blender/scripts/build_millford.py
Never run against an unsaved interactive scene: this builder starts from an empty scene.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
for name in ('exports','previews'): (OUT/name).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.unit_settings.length_unit='METERS'
scene['Design revision']='Millford V2 / dimensional blockout 01'
scene['Coordinate convention']='X east, Y north toward Maldek, Z up; lower FFL 0 m; upper FFL 4 m.'
scene['Status']='Editable spatial study. Not gameplay-tested in UE5.'
COLS={}
def collection(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); COLS[name]=c; return c
for n in ['01_Upper_Platform','02_Control_Room','03_Waiting_Hall','04_Lower_Drive','05_Generator_Room','06_Stairs_and_Landings','07_Overlook','08_Fuel_Yard','09_Relay_and_Paths','10_Parking_and_Arrival','11_Doors','12_Gondola','13_Roofs','14_Site_Structure','90_References','91_Labels','92_Cameras_Lights','93_Upper_Scale_References']:
    collection(n)
MATS={}
def mat(name,rgba,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=rgba; p.inputs['Roughness'].default_value=.78; p.inputs['Metallic'].default_value=metal
    MATS[name]=m; return m
mat('Concrete_Warm',(.48,.43,.32,1)); mat('Concrete_Service',(.24,.39,.41,1)); mat('Deck',(.40,.45,.30,1)); mat('Steel',(.12,.17,.18,1),.35); mat('Timber',(.29,.19,.105,1)); mat('Glass_Proxy',(.28,.54,.61,1)); mat('Safety_Amber',(.92,.60,.17,1)); mat('Gondola_Red',(.50,.15,.10,1)); mat('Ground',(.15,.19,.15,1)); mat('Paper',(.82,.83,.70,1)); mat('Human',(.88,.40,.13,1)); mat('Route',(.47,.56,.41,1))
GEOMETRY=[]; COLLIDERS=[]; BOXES=[]; DOORS=[]; STAIRS=[]; ROUTES={}; TEXT=[]
def register(o,name,col,material,collision=True,export=True):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    COLS[col].objects.link(o)
    if material: o.data.materials.append(MATS[material]); o.color=MATS[material].diffuse_color
    o['export_geometry']=export; o['collision']=collision
    if export: GEOMETRY.append(o)
    if collision: COLLIDERS.append(o)
    return o

def cube(name,loc,size,col,material='Concrete_Warm',collision=True,export=True):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    register(o,name,col,material,collision,export)
    if collision: BOXES.append(o)
    return o

def slab(name,x0,x1,y0,y1,z,col,material='Deck',thick=.3):
    return cube(name,((x0+x1)/2,(y0+y1)/2,z-thick/2),(x1-x0,y1-y0,thick),col,material)

def cylinder(name,loc,radius,depth,col,material='Steel',rotation=None,collision=True,export=True,vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object
    if rotation: o.rotation_euler=rotation; bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return register(o,name,col,material,collision,export)

def beam(name,a,b,width,col,material='Steel',collision=False):
    a,b=Vector(a),Vector(b); o=cube(name,(a+b)/2,(width,width,(b-a).length),col,material,collision)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def wall(name,axis,fixed,start,end,base,height,col,openings=(),material='Concrete_Warm',thick=.22):
    """Openings: (center,width,sill,height). Segmented closed boxes preserve door/window holes."""
    cursor=start
    for center,width,sill,oh in sorted(openings):
        lo,hi=center-width/2,center+width/2
        assert start<=lo<hi<=end,(name,lo,hi,start,end)
        def segment(a,b,z,h,suffix):
            if b-a<.001 or h<.001: return
            loc=((a+b)/2,fixed,z+h/2) if axis=='X' else (fixed,(a+b)/2,z+h/2)
            dims=(b-a,thick,h) if axis=='X' else (thick,b-a,h)
            cube(name+suffix,loc,dims,col,material)
        segment(cursor,lo,base,height,'_Pier')
        segment(lo,hi,base,sill,'_Sill')
        segment(lo,hi,base+sill+oh,height-sill-oh,'_Lintel')
        if sill==0: DOORS.append(dict(name=name,axis=axis,fixed=fixed,center=center,width=width,height=oh,base=base))
        cursor=hi
    if end-cursor>.001:
        loc=((cursor+end)/2,fixed,base+height/2) if axis=='X' else (fixed,(cursor+end)/2,base+height/2)
        dims=(end-cursor,thick,height) if axis=='X' else (thick,end-cursor,height)
        cube(name+'_End',loc,dims,col,material)

def rail(name,a,b,z,col):
    a,b=Vector((a[0],a[1],z)),Vector((b[0],b[1],z)); d=b-a
    beam(name+'_Top',a+Vector((0,0,1.1)),b+Vector((0,0,1.1)),.055,col)
    beam(name+'_Mid',a+Vector((0,0,.55)),b+Vector((0,0,.55)),.035,col)
    for i in range(math.ceil(d.length/1.5)+1):
        t=i/math.ceil(d.length/1.5); p=a+d*t; beam(name+'_Post',p,p+Vector((0,0,1.1)),.055,col)
    # One simplified convex guard volume. It does not close any passage left between runs.
    o=cube(name+'_Collision',(a+b)/2+Vector((0,0,.55)),(.10,d.length,1.1),col,'Steel',True,False)
    o.rotation_euler[2]=-math.atan2(d.x,d.y); o.hide_render=True; o.hide_set(True); o.display_type='WIRE'
    o['collision_only']=True

def text(name,body,loc,size=.28,rotation=(0,0,0),material='Paper'):
    data=bpy.data.curves.new(name,'FONT'); data.body=body; data.size=size; data.align_x='CENTER'; data.extrude=.001
    o=bpy.data.objects.new(name,data); COLS['91_Labels'].objects.link(o); o.location=loc; o.rotation_euler=rotation; data.materials.append(MATS[material]); TEXT.append(o); return o

def ramp(name,points,width,col='09_Relay_and_Paths'):
    # Each prism has a sloping top; the plan footprint remains exactly width wide.
    for i,(a,b) in enumerate(zip(points,points[1:])):
        a,b=Vector(a),Vector(b); delta=b-a; cross=Vector((-delta.y,delta.x,0)).normalized()*width/2
        top=[a-cross,a+cross,b+cross,b-cross]; verts=[tuple(v) for v in top]+[tuple(v-Vector((0,0,.18))) for v in top]
        faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        mesh=bpy.data.meshes.new(name+str(i)); mesh.from_pydata(verts,[],faces); mesh.update()
        o=bpy.data.objects.new(name+str(i),mesh); COLS[col].objects.link(o)
        register(o,name+f'_{i:02}',col,'Route',True,True)
    for i,p in enumerate(points[1:-1]): slab(name+f'_Joint{i}',p[0]-width/2,p[0]+width/2,p[1]-width/2,p[1]+width/2,p[2],col,'Route',.18)

def stair(name,x,y0,y1,z0,z1,width=1.6,col='06_Stairs_and_Landings'):
    # Straight flight, 24 risers x 166.7 mm; 23 going intervals x 280 mm.
    n=24; rise=(z1-z0)/n; tread=abs(y1-y0)/(n-1); direction=1 if y1>y0 else -1
    assert abs(abs(rise)-4/24)<1e-6
    for i in range(n-1):
        top=z0+rise*(i+1); yc=y0+direction*tread*(i+.5)
        # Solid box below each tread; export collision uses these individual convex boxes.
        low=min(z0,z1)-.2
        cube(name+f'_Tread_{i+1:02}',(x,yc,(top+low)/2),(width,tread+.001,top-low),col,'Concrete_Service')
        cube(name+f'_Nosing_{i+1:02}',(x,y0+direction*tread*i,top+.003),(width,.035,.006),col,'Safety_Amber',False)
    for side in [-1,1]:
        beam(name+'_Handrail',(x+side*(width/2+.04),y0,z0+1.05),(x+side*(width/2+.04),y1,z1+1.05),.055,col)
        for i in range(0,n,4):
            t=i/(n-1); p=(x+side*(width/2+.04),y0+(y1-y0)*t,z0+(z1-z0)*t)
            beam(name+'_Post',p,(p[0],p[1],p[2]+1.05),.05,col)
    STAIRS.append(dict(name=name,x=x,y0=y0,y1=y1,z0=z0,z1=z1,width=width,risers=n,riser_m=abs(rise),going_m=tread))

# LOWER LEVEL: continuous ground floor, single shared partition, clear 3.65 m to upper slab.
slab('Drive_Floor',-2,6,0,7,0,'04_Lower_Drive','Concrete_Service')
slab('Generator_Floor',-2,6,-6,0,0,'05_Generator_Room','Concrete_Service')
wall('Drive_North','X',7,-2,6,0,3.65,'04_Lower_Drive',material='Concrete_Service')
wall('Drive_West','Y',-2,0,7,0,3.65,'04_Lower_Drive',material='Concrete_Service')
wall('Drive_East','Y',6,0,7,0,3.65,'04_Lower_Drive',material='Concrete_Service')
wall('Drive_Generator_Partition','X',0,-2,6,0,3.65,'04_Lower_Drive',[(2,1.4,0,2.4),(5.2,1.2,0,2.4)],'Concrete_Service')
wall('Generator_West','Y',-2,-6,0,0,3.4,'05_Generator_Room',material='Concrete_Service')
wall('Generator_South','X',-6,-2,6,0,3.4,'05_Generator_Room',material='Concrete_Service')
wall('Generator_East','Y',6,-6,0,0,3.4,'05_Generator_Room',[(-3,1.4,0,2.4),(-.6,1.2,0,2.4)],'Concrete_Service')
wall('Stair_Vestibule_South','X',-1.2,4.4,6,0,3.4,'05_Generator_Room',material='Concrete_Service')
wall('Stair_Vestibule_West','Y',4.4,-1.2,0,0,3.4,'05_Generator_Room',material='Concrete_Service')
# UPPER DECK: exclude both stairwell and gondola bay from the slab.
slab('Platform_Main',-8,6,0,5,4,'01_Upper_Platform')
slab('Platform_NW',-8,-1.8,5,7,4,'01_Upper_Platform')
slab('Platform_NE',1.8,6,5,7,4,'01_Upper_Platform')
slab('Internal_Stair_Top',6,8,6.8,8.4,4,'06_Stairs_and_Landings')
slab('Platform_North_Link',3.6,6,7,8.4,4,'01_Upper_Platform')
slab('Hall_Covered_Link',-15,-8,0,3,4,'03_Waiting_Hall')
slab('Control_Floor',-8,-3,-4,0,4,'02_Control_Room','Concrete_Warm')
slab('Hall_Floor',-15,-8,-6,0,4,'03_Waiting_Hall','Concrete_Warm')
# PUBLIC SHELL: 3.1 m clear ceiling, actual door lintels and north-facing booth glazing.
wall('Control_North','X',0,-8,-3,4,3.1,'02_Control_Room',[(-6.1,3.0,1.0,1.4),(-3.8,1.2,0,2.4)])
wall('Control_East','Y',-3,-4,0,4,3.1,'02_Control_Room')
wall('Control_South','X',-4,-8,-3,4,3.1,'02_Control_Room')
wall('Control_Hall_Shared','Y',-8,-4,0,4,3.1,'02_Control_Room',[(-2,1.2,0,2.4)])
wall('Hall_East_Extension','Y',-8,-6,-4,4,3.1,'03_Waiting_Hall')
wall('Hall_West','Y',-15,-6,0,4,3.1,'03_Waiting_Hall')
wall('Hall_North','X',0,-15,-8,4,3.1,'03_Waiting_Hall',[(-11.5,1.6,0,2.4)])
wall('Hall_South','X',-6,-15,-8,4,3.1,'03_Waiting_Hall',[(-11.5,1.6,0,2.4)])
glass=cube('Control_Glass',(-6.1,0,5.7),(3.0,.035,1.4),'02_Control_Room','Glass_Proxy',False,False)
glass.hide_render=True; glass.hide_set(True); glass.display_type='WIRE'
# Structural posts are outside door and stair clearances.
for x,y in [(-7.8,-3.8),(-7.8,2.8),(-14.8,-5.8),(-14.8,2.8),(-3.2,-3.8),(-3.2,6.8)]:
    cube('Upper_Support',(x,y,1.7),(.28,.28,4),'14_Site_Structure','Concrete_Service')
# STAIR FLIGHTS and lower landing/cross passages.
stair('Internal',7,.36,6.8,0,4)
slab('Internal_Lower_Landing',6,8,-1.2,.36,0,'06_Stairs_and_Landings','Concrete_Service')
# Foot landing connects west through the enclosed vestibule into the drive room.
slab('Fuel_Yard',8,15,-6,0,0,'08_Fuel_Yard','Concrete_Service')
slab('Generator_Yard_Link',6,8,-3.9,-2.1,0,'08_Fuel_Yard','Concrete_Service')
stair('Exterior',16.3,-4.5,1.94,0,4)
slab('Exterior_Lower_Landing',15,17.3,-6,-4.5,0,'06_Stairs_and_Landings','Concrete_Service')
slab('Exterior_Upper_Landing',15,17.3,1.94,3.6,4,'06_Stairs_and_Landings')
slab('Overlook',9,15,2,6.5,4,'07_Overlook')
# A bridge crosses above the internal stair's high end, never above its low-headroom segment.
slab('Overlook_Bridge',8,10,6.8,8.4,4,'07_Overlook')
slab('Overlook_North_Link',9,11,6.5,8.4,4,'07_Overlook')
# Accessible exterior cycle: platform north landing -> bridge -> overlook -> exterior stair.
rail('Platform_North_West',(-8,7),(-1.8,7),4,'01_Upper_Platform')
rail('Platform_North_East',(1.8,8.4),(10,8.4),4,'01_Upper_Platform')
rail('Platform_South',(-3,0),(6,0),4,'01_Upper_Platform')
rail('Stairwell_West',(6,.2),(6,6.5),4,'06_Stairs_and_Landings')
rail('Stairwell_East',(8,.2),(8,6.5),4,'06_Stairs_and_Landings')
rail('Overlook_North',(11,6.5),(14,6.5),4,'07_Overlook')
rail('Overlook_South',(9,2),(15,2),4,'07_Overlook')
# Leave the forest-path connection open at the east edge y4.2..5.8.
rail('Overlook_East_North',(15,5.8),(15,6.5),4,'07_Overlook')
rail('Hall_Link_North',(-15,3),(-8,3),4,'03_Waiting_Hall')
rail('Hall_Link_West',(-15,0),(-15,3),4,'03_Waiting_Hall')
# SIMPLE EQUIPMENT: working clearance remains around every major object.
cube('Control_Console',(-6.2,-.75,4.53),(2.4,.70,1.06),'02_Control_Room','Steel')
for i in range(4): cylinder('Console_Gauge',(-7.0+i*.5,-.75,5.09),.12,.035,'02_Control_Room','Paper',collision=False)
cube('Operator_Desk',(-6.9,-3.2,4.38),(1.6,.65,.76),'02_Control_Room','Timber')
cube('Logbook',(-6.65,-3.2,4.79),(.32,.23,.055),'02_Control_Room','Paper',False)
cube('Radio',(-7.45,-3.2,4.9),(.36,.22,.23),'02_Control_Room','Steel',False)
cube('Ticket_Counter',(-13.7,-1.5,4.5),(1.9,.75,1),'03_Waiting_Hall','Timber')
for y in [-2.5,-4.5]: cube('Waiting_Bench',(-13.7,y,4.23),(1.8,.48,.46),'03_Waiting_Hall','Timber')
cube('Drive_Motor',(1.0,4.4,.75),(2.4,1.3,1.5),'04_Lower_Drive','Steel')
cylinder('Drive_Flywheel',(3.0,4.4,1.0),.7,.3,'04_Lower_Drive','Safety_Amber',rotation=(0,math.pi/2,0))
cube('Local_Gauge_Cabinet',(5.6,3.3,1),(.4,.75,2),'04_Lower_Drive','Steel')
cube('Generator',(0,-3.7,.75),(2.4,1.2,1.5),'05_Generator_Room','Steel')
cube('Workbench',(3.5,-5.35,.45),(2.4,.7,.9),'05_Generator_Room','Timber')
cube('Operator_Locker',(-1.4,-1.4,1),(.55,.7,2),'05_Generator_Room','Steel')
cube('Breaker_Panel',(5.2,-5.7,1.35),(.8,.3,1.2),'05_Generator_Room','Steel')
cylinder('Bulk_Diesel_Tank',(11.6,-4.6,1.05),.7,3,'08_Fuel_Yard','Steel',rotation=(0,math.pi/2,0))
for x in [10.6,12.6]: cube('Tank_Saddle',(x,-4.6,.25),(.35,1.4,.5),'08_Fuel_Yard','Concrete_Service')
cylinder('Binocular_Stand',(12.4,5.9,4.65),.055,1.3,'07_Overlook')
cube('Binocular_Head',(12.4,5.9,5.35),(.45,.28,.18),'07_Overlook','Steel',False)
# OUTBUILDING AND SLOPING ROUTES: deliberately coarse until the core station is walked.
slab('Relay_Floor',24,28,-1,3,2,'09_Relay_and_Paths','Concrete_Service')
wall('Relay_South','X',-1,24,28,2,2.8,'09_Relay_and_Paths',[(26,1.2,0,2.3)],'Concrete_Service')
wall('Relay_North','X',3,24,28,2,2.8,'09_Relay_and_Paths',[(26,1.2,0,2.3)],'Concrete_Service')
for x in [24,28]: wall('Relay_Side','Y',x,-1,3,2,2.8,'09_Relay_and_Paths',material='Concrete_Service')
cube('Relay_Cabinet',(24.5,.7,3),(.55,1.8,2),'09_Relay_and_Paths','Steel')
ramp('Fuel_To_Relay',[(14,-6,0),(18.5,-7,0),(21,-6,.4),(26,-4,1),(26,-1,2)],1.6)
ramp('Relay_To_Overlook',[(26,3,2),(26,10,3),(19,11,4),(15,5,4)],1.6)
slab('Parking',-21,-13,-18,-12,-1,'10_Parking_and_Arrival','Ground')
slab('Arrival_Upper_Landing',-12.5,-10.5,-7.5,-6,4,'10_Parking_and_Arrival')
stair('Arrival',-11.5,-13.94,-7.5,0,4,1.6,'10_Parking_and_Arrival')
slab('Arrival_Lower_Landing',-12.5,-10.5,-15.5,-13.94,0,'10_Parking_and_Arrival','Ground')
ramp('Parking_To_Stair',[(-13,-15,-1),(-11.5,-15,0)],1.6,'10_Parking_and_Arrival')
cube('Parked_Car',(-18,-15,-.35),(1.8,3.8,1.3),'10_Parking_and_Arrival','Steel')
# GONDOLA: shell with an actual 1.2 m south opening and bench clearance.
slab('Gondola_Floor',-1.55,1.55,5.05,8.85,4,'12_Gondola','Gondola_Red',.12)
wall('Gondola_South','X',5.05,-1.55,1.55,4,2.3,'12_Gondola',[(0,1.2,0,2.1)],'Gondola_Red',.09)
wall('Gondola_North','X',8.85,-1.55,1.55,4,2.3,'12_Gondola',[(0,2.4,.9,1.15)],'Gondola_Red',.09)
for x in [-1.55,1.55]:
    wall('Gondola_Side','Y',x,5.05,8.85,4,2.3,'12_Gondola',[(6.95,2.7,.9,1.15)],'Gondola_Red',.09)
    cube('Gondola_Bench',(x-math.copysign(.28,x),7,.24+4),(.44,2.4,.48),'12_Gondola','Timber')
slab('Gondola_Roof',-1.6,1.6,5,8.9,6.4,'13_Roofs','Gondola_Red',.10)
beam('Gondola_Hanger',(0,7,6.4),(0,7,8),.1,'12_Gondola')
beam('Cable_Ascending',(0,7,8),(0,45,18),.035,'01_Upper_Platform')
# Open hinged placeholders remain independently editable / exportable.
def door_leaf(name,hinge,width,height,angle):
    o=cube(name,(hinge[0]+width/2,hinge[1],hinge[2]+height/2),(width,.06,height),'11_Doors','Timber')
    # Rebase mesh onto hinge before rotation.
    shift=Vector((width/2,0,height/2)); o.data.transform(Matrix.Translation(shift)); o.location=hinge; o.rotation_euler[2]=angle
    o['hinge_pivot']=True; o['open_angle_degrees']=math.degrees(angle)
    return o
# Leaves are positioned against the inside wall, outside the clear aperture.
door_leaf('Door_Control_Platform',(-4.4,-.18,4),1.15,2.35,-math.pi/2)
door_leaf('Door_Generator_Yard',(6.18,-3.7,0),1.35,2.35,0)
# CEILINGS / CANOPY: own collection permits dollhouse and assembled inspection.
slab('Control_Roof',-8.2,-2.8,-4.2,.2,7.35,'13_Roofs','Concrete_Warm',.25)
slab('Hall_Roof',-15.2,-8,-6.2,3.1,7.5,'13_Roofs','Timber',.25)
slab('Generator_Roof',-2.15,6.15,-6.15,0,3.65,'13_Roofs','Concrete_Service',.25)
slab('Relay_Roof',23.8,28.2,-1.2,3.2,5.05,'13_Roofs','Concrete_Service',.25)
for x0,x1 in [(-8,-2),(2,8)]: slab('Platform_Canopy',x0,x1,0,7.1,7.6,'13_Roofs','Timber',.18)
slab('Canopy_Front',-2,2,0,4.8,7.6,'13_Roofs','Timber',.18)
for x,y in [(-7.7,6.7),(5.65,6.65),(-7.7,.4),(5.65,.4)]:
    beam('Canopy_Post',(x,y,4),(x,y,7.5),.16,'01_Upper_Platform','Steel',True)
# Presentation base below playable geometry; isolated from exports and clearance checks.
slab('Site_Presentation_Plinth',-24,31,-21,15,-1.45,'90_References','Ground',.25)['export_geometry']=False
# Remove plinth from production records: reference only.
plinth=bpy.data.objects['Site_Presentation_Plinth']; GEOMETRY.remove(plinth); COLLIDERS.remove(plinth); BOXES.remove(plinth)
# Human scale references: 1.80 m height, 1.65 m eye markers.
def human(name,x,y,z):
    cylinder(name+'_LegL',(x-.11,y,z+.40),.08,.8,'90_References','Human',collision=False,export=False)
    cylinder(name+'_LegR',(x+.11,y,z+.40),.08,.8,'90_References','Human',collision=False,export=False)
    cube(name+'_Torso',(x,y,z+1.13),(.42,.23,.65),'90_References','Human',False,False)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.145,location=(x,y,z+1.655)); register(bpy.context.object,name+'_Head','90_References','Human',False,False)
    for side in [-1,1]: beam(name+'_Arm',(x+side*.25,y,z+1.38),(x+side*.28,y,z+.85),.11,'90_References','Human',False)
    for o in COLS['90_References'].objects:
        if o.name.startswith(name) and o in GEOMETRY: GEOMETRY.remove(o); o['export_geometry']=False
human('Operator',-6.5,-1.6,4); human('Platform_Person',2,2,4); human('Service_Person',3,-1.5,0)
for o in list(COLS['90_References'].objects):
    if o.name.startswith(('Operator','Platform_Person')):
        COLS['90_References'].objects.unlink(o); COLS['93_Upper_Scale_References'].objects.link(o)
# One-metre reference cube, exported separately for scale checks.
cube('SM_Scale_1m',(-21,-19,-.95),(1,1,1),'90_References','Safety_Amber',False,False)
for name,body,pos in [
 ('Title','MILLFORD STATION  /  BLOCKOUT 01',(-7,-19.7,-1.15)),
 ('Sub','V2 DIMENSIONAL STUDY     |     METRES     |     NORTH +Y',(-7,-20.5,-1.15)),
 ('Control_Label','CONTROL  5 x 4 m',(-5.5,-3.4,4.02)),
 ('Hall_Label','WAITING HALL  7 x 6 m',(-11.5,-5.4,4.02)),
 ('Platform_Label','PLATFORM  +4.00 m',(-2,1.1,4.02)),
 ('Drive_Label','DRIVE  8 x 7 m',(1.6,1.8,.02)),
 ('Generator_Label','GENERATOR  8 x 6 m',(2,-4.9,.02)),
 ('Fuel_Label','FUEL YARD',(11.5,-.8,.02)),
 ('Relay_Label','RELAY',(26,1.8,2.02)),
 ('Overlook_Label','OVERLOOK',(12,3.3,4.02))]: text(name,body,pos,.25 if name!='Title' else .48)
# Cameras support meaningful review positions as well as an overall plan.
def camera(name,loc,target,lens=40,ortho=None):
    data=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,data); COLS['92_Cameras_Lights'].objects.link(o); o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); data.lens=lens; data.clip_end=300
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    return o
cams={}
cams['Overview']=camera('CAM_01_Overview',(40,-48,39),(2,-1,2),ortho=65)
cams['Plan']=camera('CAM_02_Plan',(2,-2,70),(2,-2,0),ortho=59)
cams['Operator']=camera('CAM_03_Operator_Eye',(-6.5,-1.6,5.65),(0,7,5.25),lens=19)
cams['Fuel']=camera('CAM_04_Fuel_Return',(14,-8,1.65),(3,2,4.5),lens=23)
cams['Lower']=camera('CAM_05_Lower_Service',(17,-17,13),(1,-.5,1),ortho=30)
scene.camera=cams['Overview']
# Three useful view layers; saved with cutaway active, no exploded transforms baked into geometry.
base=bpy.context.view_layer; base.name='01_Cutaway'
base.layer_collection.children['13_Roofs'].exclude=True
full=scene.view_layers.new('02_Full_Shell')
service=scene.view_layers.new('03_Lower_Level')
for n in ['01_Upper_Platform','02_Control_Room','03_Waiting_Hall','07_Overlook','12_Gondola','13_Roofs','91_Labels','93_Upper_Scale_References','14_Site_Structure']:
    service.layer_collection.children[n].exclude=True
bpy.data.objects['Door_Control_Platform'].hide_set(True,view_layer=service)
# Workbench is portable and deliberately communicates a blockout rather than final art.
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.studiolight_rotate_z=.45
scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.3; scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.background_type='WORLD'; scene.world.color=(.055,.065,.057)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
# Configure the opening Blender viewport for immediate editing.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active; sp.clip_end=300; sp.shading.type='SOLID'; sp.shading.color_type='MATERIAL'; sp.shading.show_cavity=True; sp.overlay.show_overlays=False
            sp.region_3d.view_distance=56; sp.region_3d.view_location=(2,-1,2); sp.region_3d.view_rotation=cams['Overview'].rotation_euler.to_quaternion(); sp.region_3d.view_perspective='ORTHO'
# Embed production notes in the .blend.
notes=bpy.data.texts.new('START_HERE')
notes.write('MILLFORD V2 — DIMENSIONAL BLOCKOUT 01\n\nMetric scene: 1 Blender unit = 1 metre. Upper FFL +4 m; lower FFL 0 m.\nView layers: 01_Cutaway / 02_Full_Shell / 03_Lower_Level.\nCameras: overview, plan, operator eye, fuel return, lower service.\nCollections 01–14 contain editable geometry. 90–92 are reference/presentation only.\nDoors have hinge origins and remain separate. Roofs can be toggled as a collection.\nNo UE5 gameplay validation yet. See BLOCKOUT_README.md for export/import instructions and known limitations.\nDo not rerun the builder over hand edits: the generator rebuilds from scratch. Save your edited scene under a new revision name.\n')
gondola_root=bpy.data.objects.new('Gondola_MOVE_THIS',None)
COLS['12_Gondola'].objects.link(gondola_root); gondola_root.location=(0,6.95,4)
bpy.context.view_layer.update()
for o in list(COLS['12_Gondola'].objects)+[bpy.data.objects['Gondola_Roof']]:
    if o==gondola_root: continue
    world=o.matrix_world.copy(); o.parent=gondola_root; o.matrix_world=world
# Export copies are generated in a temporary scene, leaving the editable source untouched.
bpy.context.view_layer.update()
manifest={'revision':'v2_blockout_01','blender':bpy.app.version_string,'units':'metres','upper_floor_m':4,'lower_floor_m':0,'stairs':STAIRS,'openings':DOORS,'files':[]}
(OUT/'blockout_dimensions.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_blockout_01.blend'))
print('BUILD_SAVED',len(GEOMETRY),'render objects',len(COLLIDERS),'colliders',flush=True)
# Write export data before launching the independent exporter / validator.
for o in COLLIDERS: o['collision']=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_blockout_01.blend'))
for key,layer in [('Overview','01_Cutaway'),('Plan','01_Cutaway'),('Operator','02_Full_Shell'),('Lower','03_Lower_Level')]:
    scene.camera=cams[key]; scene.render.filepath=str(OUT/'previews'/f'{key.lower()}.png')
    for vl in scene.view_layers: vl.use=(vl.name==layer)
    for o in COLS['93_Upper_Scale_References'].objects:
        if o.name.startswith('Operator'): o.hide_render=(key=='Operator')
    bpy.data.objects['Door_Control_Platform'].hide_render=(key=='Lower')
    bpy.ops.render.render(write_still=True,layer=layer)
scene.camera=cams['Overview']
for o in COLS['93_Upper_Scale_References'].objects:
    if o.name.startswith('Operator'): o.hide_render=False
bpy.data.objects['Door_Control_Platform'].hide_render=False
for vl in scene.view_layers: vl.use=(vl.name=='01_Cutaway')
bpy.context.window.view_layer=scene.view_layers['01_Cutaway']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_blockout_01.blend'))
print('BUILD_COMPLETE',flush=True)
