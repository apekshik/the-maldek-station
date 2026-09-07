"""Patch the authored source and export isolated R10 meshes; never overwrite R04."""
import bpy,json,math
from mathutils import Vector,Matrix
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';(out/'fbx').mkdir(parents=True,exist_ok=True)
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
def box(name,p,s,mat='R04_Galvanized_Fittings',col='01_Upper_Platform',collision=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[col].objects.link(o);o.data.materials.append(bpy.data.materials.get(mat) or bpy.data.materials.get('Steel'));o['collision']=collision;return o
def rail(x0,x1,y):
 for z in [4.55,5.1]:box('R10_Guard',((x0+x1)/2,y,z),(x1-x0,.055,.055))
 for x in [x0,x1]:
  box('R10_Post',(x,y,4.55),(.06,.06,1.1));box('R10_Post_Foot',(x,y,4.015),(.18,.18,.03))
 c=box('R10_Guard_Collision',((x0+x1)/2,y,4.55),(x1-x0,.08,1.1));c.hide_render=True
# Replace the two uninterrupted transverse guards, including their sockets/bolts.
removed=[]
for o in list(bpy.data.collections['01_Upper_Platform'].objects):
 lo,hi=bounds(o)
 boundary=(abs((lo[1]+hi[1])/2-7)<.13 and hi[0]<=-1.7 and hi[2]>4.1) or (abs((lo[1]+hi[1])/2-8.4)<.13 and lo[0]>=1.7 and hi[2]>4.1)
 if o.name.startswith(('Platform_North_West','Platform_North_East')) or (o.name.startswith('R04_') and boundary):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
rail(-8,-4.05,7);rail(3.65,10,8.4)
# Fill the unplanned eastern floor opening next to the machinery well.
box('R10_Dock_Infill',(2.65,6.7,3.94),(1.9,3.4,.12))
for x in [-1.73,1.73]:box('R10_Cabin_Threshold_Edge',(x,8.1,3.97),(.16,6.2,.06))
# The east stairwell rail has no floor beneath it. Keep actual sloping stair handrails.
for o in list(bpy.data.collections['06_Stairs_and_Landings'].objects):
 if o.name.startswith('Stairwell_East'):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Enlarge the ticket/waiting hall outward, preserving its shared control-room wall.
hall=[]
for o in bpy.data.collections['03_Waiting_Hall'].objects:
 if o.type!='MESH':continue
 # Affine world-space transform, leaving x=-8 and the front facade y=0 fixed.
 A=Matrix.Translation(Vector((-8,0,0)))@Matrix.Diagonal((1.4,1.3,1,1))@Matrix.Translation(Vector((8,0,0)))
 o.matrix_world=A@o.matrix_world;hall.append(o.name)
for o in bpy.data.collections['13_Roofs'].objects:
 if o.type=='MESH':
  lo,hi=bounds(o)
  if hi[0]<-7 and lo[0]<-14:o.matrix_world=A@o.matrix_world
# Arrival stairs align with the shifted rear ticket-hall doorway. Parking moves 50m away.
for o in bpy.data.collections['10_Parking_and_Arrival'].objects:
 if o.name.startswith(('Parking','Parked_Car')):o.location+=Vector((-19,-45,0))
 elif o.name.startswith('Arrival'):o.location.x-=1.4;o.location.y-=1.8
 if o.name.startswith('Parking_To_Stair'):o.hide_render=True;o['collision']=False
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'station_patched.blend'))
# Reuse the established evaluated-mesh/UCX exporter with a scoped output directory.
source=Path(__file__).with_name('export_station.py').read_text()
source=source.replace("OUT=Path(__file__).resolve().parents[1]","OUT=Path(__file__).resolve().parents[1]/'revision10'")
source=source.replace("  if col.name=='13_Roofs' and o.matrix_world.translation.x>25:continue","")
source=source.replace("collections=[c for c in bpy.data.collections if re.match(r'^(0[1-8]|1[0-4]|18)_',c.name)]","collections=[bpy.data.collections[n] for n in ['01_Upper_Platform','03_Waiting_Hall','06_Stairs_and_Landings','10_Parking_and_Arrival','13_Roofs']]")
exec(compile(source,'export_station.py','exec'),{'__file__':__file__})
(out/'mesh_changes.json').write_text(json.dumps({'removed':removed,'hall_width_m':9.8,'hall_depth_m':7.8,'parking_offset_m':[-19,-45,0],'arrival_stair_offset_m':[-1.4,-1.8,0]},indent=2))
