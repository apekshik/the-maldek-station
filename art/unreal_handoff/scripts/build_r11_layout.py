"""Authored bridge/lookout and separated lower maintenance destination, in metres."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'revision11';(out/'fbx').mkdir(parents=True,exist_ok=True)
terrain=json.loads((out/'terrain_grid.json').read_text()) if (out/'terrain_grid.json').exists() else json.loads((out.parent/'revision10/terrain_grid.json').read_text())
def ground(x,y):
 i=int(x-terrain['xmin']);j=int(y-terrain['ymin']);u=x-terrain['xmin']-i;v=y-terrain['ymin']-j;n=terrain['nx'];a=terrain['vertices'];return a[j*n+i][2]*(1-u)*(1-v)+a[j*n+i+1][2]*u*(1-v)+a[(j+1)*n+i][2]*(1-u)*v+a[(j+1)*n+i+1][2]*u*v
for n in ['20_Lookout_Bridge','21_Maintenance']:
 if n not in bpy.data.collections:
  c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c)
col='20_Lookout_Bridge'
steel='R02_Chipped_Painted_Steel';zinc='R04_Galvanized_Fittings';concrete='R02_Weathered_Concrete';timber='R02_Damp_Timber'
def put(o,name,material,collision=False):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[col].objects.link(o);o['collision']=collision;o['export_geometry']=True
 if material:o.data.materials.append(bpy.data.materials.get(material) or bpy.data.materials['R02_Chipped_Painted_Steel'])
 return o
def box(name,p,s,material=steel,collision=False):
 me=bpy.data.meshes.new(name);me.from_pydata([(sx*s[0]/2,sy*s[1]/2,sz*s[2]/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.location=p;return put(o,name,material,collision)
def beam(name,a,b,width=.065,material=steel):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,width,(b-a).length),material);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def guard(a,b):
 a,b=Vector(a),Vector(b);d=b-a
 for h in [.55,1.1]:beam('Guard_Rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.055,zinc)
 for j in range(math.ceil(d.length/1.5)+1):
  p=a+d*j/math.ceil(d.length/1.5);beam('Guard_Post',p,p+Vector((0,0,1.1)),.065,zinc);box('Bolted_Base',p+Vector((0,0,.015)),(.18,.18,.03),zinc)
 o=box('Guard_Collision',(a+b)/2+Vector((0,0,.55)),(.08,d.length,1.1),None,True);o.rotation_euler.z=-math.atan2(d.x,d.y);o.hide_render=True
def grated(a,b,width):
 a,b=Vector(a),Vector(b);d=b-a;n=Vector((-d.y,d.x,0)).normalized();axis=d.normalized();length=d.length;verts=[];faces=[]
 def bar(p,w,l,h):
  k=len(verts)
  for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:verts.append(tuple(p+n*sx*w/2+axis*sy*l/2+Vector((0,0,sz*h/2))))
  faces.extend([tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 for i in range(math.ceil(width/.09)+1):bar((a+b)/2+n*(-width/2+width*i/math.ceil(width/.09))-Vector((0,0,.025)),.016,length,.05)
 for j in range(math.ceil(length/.32)+1):bar(a+d*j/math.ceil(length/.32)-Vector((0,0,.02)),width,.016,.035)
 me=bpy.data.meshes.new('Open_Grating');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Open_Grating',me);bpy.context.collection.objects.link(o);put(o,'Open_Grating',zinc)
 plate=box('Grating_Collision',(a+b)/2-Vector((0,0,.045)),(width,length,.09),None,True);plate.rotation_euler.z=-math.atan2(d.x,d.y);plate.hide_render=True
 for side in [-1,1]:
  p=a+n*side*width/2;q=b+n*side*width/2;beam('Edge_Channel',p-Vector((0,0,.15)),q-Vector((0,0,.15)),.18);guard(p,q)
 for j in range(math.ceil(length/2)+1):
  p=a+d*j/math.ceil(length/2);beam('Cross_Beam',p-n*(width/2+.12)-Vector((0,0,.21)),p+n*(width/2+.12)-Vector((0,0,.21)),.14)
 return n
# Keep the existing circulation landing, but move its destination and binoculars out.
for o in list(bpy.data.collections['07_Overlook'].objects):
 if o.name.startswith(('Overlook_North','Binocular')):
  if o.name.startswith('Binocular'):
   o.location+=Vector((6.6,28.4,0));put(o,o.name,steel)
  else:bpy.data.objects.remove(o,do_unlink=True)
box('Lookout_Junction_Extension',(12,7.45,3.85),(6,1.9,.3),concrete,True)
guard((9,8.4,4),(11.1,8.4,4));guard((12.9,8.4,4),(15,8.4,4));guard((15,6.5,4),(15,8.4,4))
bridge=[(12,8.35,4),(16,15,4),(19,31.12,4)]
for a,b in zip(bridge,bridge[1:]):grated(a,b,1.5)
# A 5 x 6m lookout at the far end, with an open rear entry.
grated((19,31,4),(19,37,4),5)
guard((16.5,37,4),(21.5,37,4));guard((16.5,31,4),(18.12,31,4));guard((19.88,31,4),(21.5,31,4))
for x in [16.7,21.3]:
 beam('Lookout_Lower_Girder',(x,31,2.8),(x,37,2.8),.24)
 for y in [31,34,37]:beam('Lookout_Bracing',(x,y,2.8),(x,min(y+3,37),3.8),.12)
# Triangulated bridge structure and rock anchors; supports stop on the authored cliff face.
for x in [11.3,12.7]:
 z=ground(x,7);beam('Bridge_Anchor_Strut',(x,7,z),(x,10.5,3.75),.24);box('Bridge_Rock_Anchor',(x,7,z),(.65,.45,.65),concrete)
for a,b in zip(bridge,bridge[1:]):
 a,b=Vector(a),Vector(b);d=b-a;n=Vector((-d.y,d.x,0)).normalized()
 for side in [-1,1]:
  lo=a+n*.8*side-Vector((0,0,1.1));hi=b+n*.8*side-Vector((0,0,1.1));beam('Bridge_Lower_Chord',lo,hi,.18)
  for j in range(math.ceil(d.length/2.5)):
   p=a+d*j/math.ceil(d.length/2.5)+n*.8*side;q=a+d*(j+1)/math.ceil(d.length/2.5)+n*.8*side;beam('Bridge_Diagonal',p-Vector((0,0,1.1)),q-Vector((0,0,.1)),.09)
# Lower maintenance rooms: 6x8 generator room plus 3x5 workshop.
# Back-stayed steel towers support the long exposed span without a pier in the abyss.
for x in [11,13]:
 z=ground(x,7.5);beam('Bridge_Tower',(x,7.5,z-.2),(x,7.5,14),.25);box('Tower_Footing',(x,7.5,z),(.85,.85,.5),concrete)
 z=ground(x,1);beam('Tower_Backstay',(x,7.5,14),(x,1,z),.06);box('Backstay_Anchor',(x,1,z),(.75,.75,.5),concrete)
 endx=16.7 if x==11 else 21.3
 beam('Deck_Suspension',(x,7.5,14),(endx,36.8,3.8),.05)
 beam('Span_Suspension',(x,7.5,14),(15.3 if x==11 else 16.7,15,3.8),.045)
beam('Tower_Crosshead',(10.7,7.5,14),(13.3,7.5,14),.22)
col='21_Maintenance'
def wall(axis,fixed,start,end,openings=()):
 cursor=start
 for center,w in sorted(openings):
  lo,hi=center-w/2,center+w/2
  for a,b,z,h in [(cursor,lo,-1,3.4),(lo,hi,1.5,.9)]:
   if b>a:
    box('Service_Wall',((a+b)/2,fixed,z+h/2) if axis=='X' else (fixed,(a+b)/2,z+h/2),(b-a,.22,h) if axis=='X' else (.22,b-a,h),concrete,True)
  cursor=hi
 if end>cursor:box('Service_Wall',((cursor+end)/2,fixed,.7) if axis=='X' else (fixed,(cursor+end)/2,.7),(end-cursor,.22,3.4) if axis=='X' else (.22,end-cursor,3.4),concrete,True)
box('Generator_Floor',(30,-15,-1.16),(6,8,.32),concrete,True);box('Workshop_Floor',(34.5,-15.5,-1.16),(3,5,.32),concrete,True)
wall('Y',27,-19,-11,[(-15,1.6)]);wall('Y',33,-19,-11,[(-15.5,1.4)]);wall('X',-11,27,33);wall('X',-19,27,33,[ (30,1.5) ])
wall('Y',36,-18,-13);wall('X',-18,33,36);wall('X',-13,33,36)
box('Generator_Roof',(30,-15,2.53),(6.6,8.6,.26),steel,True);box('Workshop_Roof',(34.5,-15.5,2.53),(3.6,5.6,.26),steel,True)
for x in [27,30,33,36]:
 for y in [-19,-11] if x<34 else [-18,-13]:box('Foundation_Pier',(x,y,-2.25),(.6,.6,2.5),concrete,True)
# Move existing machinery into the new building; old room becomes service circulation.
for o in list(bpy.data.collections['05_Generator_Room'].objects):
 if o.name.startswith(('Generator','Workbench','Operator_Locker','Breaker_Panel')) and not o.name.startswith(('Generator_Floor','Generator_West','Generator_South','Generator_East')):
  o.location+=Vector((29,-11.3,-1));put(o,o.name,None,bool(o.get('collision',False)))
# Relocate tank yard contents; preserve the original exit route and its ground.
for o in list(bpy.data.collections['08_Fuel_Yard'].objects):
 if o.name.startswith(('Bulk_Diesel','Tank_Saddle')):o.location+=Vector((18.4,-17.8,-1));put(o,o.name,None,bool(o.get('collision',False)))
box('Tank_Containment_Base',(31.5,-22.5,-1.2),(9,5,.4),concrete,True)
for x in [27,36]:box('Containment_Kerb',(x,-22.5,-.8),(.22,5,.4),concrete,True)
box('Containment_Kerb',(31.5,-25,-.8),(9,.22,.4),concrete,True)
for x in [28.1,34.9]:box('Containment_Kerb',(x,-20,-.8),(2.2,.22,.4),concrete,True)
beam('Fuel_Pipe',(30,-21.2,-.55),(30,-19.2,-.55),.075)
for y in [-17,-16,-15,-14]:
 box('Workshop_Shelf',(35.5,y,.4),(.7,.8,.07),steel);box('Supply_Crate',(35.4,y,.05),(.5,.6,.55),timber,True)
# Walkable winding service route with a simple continuous collision surface.
route=[(6,-3,0),(12,-4,0),(17,-9,-.3),(22,-12,-.7),(27,-15,-1)]
for a,b in zip(route,route[1:]):
 a,b=Vector(a),Vector(b);d=b-a;n=Vector((-d.y,d.x,0)).normalized();vs=[a-n*1.25,b-n*1.25,b+n*1.25,a+n*1.25];me=bpy.data.meshes.new('Service_Path');me.from_pydata(vs,[],[(0,1,2,3)]);o=bpy.data.objects.new('Service_Path',me);bpy.context.collection.objects.link(o);put(o,'Service_Path','R03_Wet_Gravel',False)
 # Thin closed ramp is convex and exports as UCX.
 ob=box('Service_Path_Collision',(a+b)/2-Vector((0,0,.09)),(2.5,d.length+.08,.18),None,True);ob.rotation_euler=(b-a).to_track_quat('Y','Z').to_euler();ob.hide_render=True
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out/'station_layout.blend'))
source=Path(__file__).with_name('export_station.py').read_text();source=source.replace("OUT=Path(__file__).resolve().parents[1]","OUT=Path(__file__).resolve().parents[1]/'revision11'")
source=source.replace("collections=[c for c in bpy.data.collections if re.match(r'^(0[1-8]|1[0-4]|18)_',c.name)]","collections=[bpy.data.collections[n] for n in ['05_Generator_Room','07_Overlook','08_Fuel_Yard','20_Lookout_Bridge','21_Maintenance']]")
exec(compile(source,'export_station.py','exec'),{'__file__':__file__})
(out/'layout.json').write_text(json.dumps({'bridge_points':bridge,'bridge_width_m':1.5,'bridge_length_m':sum(math.dist(a,b) for a,b in zip(bridge,bridge[1:])),'lookout_bounds':[16.5,21.5,31,37,4],'service_route':route,'service_route_length_m':sum(math.dist(a,b) for a,b in zip(route,route[1:])),'generator_room_m':[6,8],'workshop_m':[3,5],'tank_yard_m':[9,5]},indent=2))
