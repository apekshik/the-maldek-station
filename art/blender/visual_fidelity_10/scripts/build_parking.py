"""VF10 parking study; preserves VF09 architecture and the existing parked car."""
import bpy, ast, math, json, random
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'visual_fidelity_09/Maldek_Service_Apron_Refinement.blend'))
s=bpy.context.scene
steel=bpy.data.materials['VF06_Structural_steel'];concrete=bpy.data.materials['VF06_Concrete'];cream=bpy.data.materials['VF06_Warm_enamel'];zinc=bpy.data.materials['VF06_Galvanized']
for n in ast.parse((OUT.parent/'visual_fidelity_01/scripts/build_sample.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['mesh','box','beam','cylinder','camera','area','material']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
group=collection('VF10_01_Parking_Ground')
gravel=material('VF10_Compacted_Gravel',(.19,.18,.145),0,.9)
old=bpy.data.objects['Parking'];bpy.data.objects.remove(old,do_unlink=True)
# Keep the present car and initial player clearance. Bays lie south of a 5.5 m lane.
box('VF10_Parking_floor',(-37.25,-58,-1.16),(14.5,12,.32),gravel,.025)
group=collection('VF10_02_Parking_Furniture')
for x in [-43,-40,-37]:
 box('VF10_Wheel_stop',(x,-62.3,-.91),(1.8,.20,.18),concrete,.035)
 for dx in [-.64,.64]:box('VF10_Stop_reflector',(x+dx,-62.405,-.88),(.16,.012,.04),cream,.003)
# Embedded narrow divider stones, avoiding painted lines on loose gravel.
for x in [-44.4,-41.5,-38.5,-35.5]:
 for y in [-61.75,-59.75]:box('VF10_Bay_divider',(x,y,-1.01),(.09,1.4,.10),concrete,.012)
# Edge curbs terminate at the vehicle and pedestrian openings.
for x in [-44.5]:box('VF10_Edge_curb',(x,-58,-.96),(.18,12,.24),concrete,.02)
box('VF10_Rear_curb',(-37.25,-64,-.96),(14.5,.18,.24),concrete,.02)
box('VF10_East_curb',(-30,-61,-.96),(.18,6,.24),concrete,.02)
box('VF10_North_curb',(-41,-52,-.96),(7,.18,.24),concrete,.02)
# Arrival information board and bench form a small pedestrian pocket beside the bays.
for x in [-33.8,-32.2]:
 box('VF10_Sign_post',(x,-61.5,.12),(.08,.08,2.24),steel,.006)
box('VF10_Arrival_sign',(-33,-61.5,.78),(1.85,.10,.75),steel,.02)
box('VF10_Sign_face',(-33,-61.436,.78),(1.67,.016,.57),cream,.008)
for text,z,size in [('MALDEK STATION',.91,.115),('<  FOOTPATH',.70,.085)]:
 d=bpy.data.curves.new('VF10_Sign_text','FONT');d.body=text;d.size=size;d.align_x='CENTER';d.extrude=.0005
 o=bpy.data.objects.new('VF10_Sign_text',d);group.objects.link(o);o.location=(-33,-61.424,z);o.rotation_euler=(math.pi/2,0,math.pi);d.materials.append(steel)
for x in [-33.7,-32.3]:box('VF10_Bench_leg',(x,-63,-.77),(.07,.38,.46),steel,.004)
box('VF10_Bench_seat',(-33,-63,-.52),(1.9,.45,.065),concrete,.018)
# Recessed trench body owns its surface; grate bars sit above the dark bed.
box('VF10_Drain_bed',(-34.8,-60.4,-1.03),(.22,5.5,.08),steel,.003)
for i in range(69):box('VF10_Drain_bar',(-34.8,-63.1+i*.08,-.985),(.22,.025,.025),zinc,.002)
# Use current R12 forest elevations as parking context, not the old Blender cliff.
terrain=bpy.data.objects['R11_Current_Terrain'];changed=0
grid=json.loads((OUT.parents[2]/'art/unreal_handoff/revision12/terrain_grid.json').read_text())['vertices']
heights={(round(x,3),round(y,3)):z for x,y,z in grid}
def ground(x,y):
 return heights.get((round(x),round(y)),-1.34)
for v in terrain.data.vertices:
 p=terrain.matrix_world@v.co
 if -51<p.x<-24 and -70<p.y<-47:p.z=heights.get((round(p.x,3),round(p.y,3)),p.z)
 d=math.hypot(max(-44.6-p.x,0,p.x+29.9),max(-64.1-p.y,0,p.y+51.9))
 if d<2:
  target=-1.34
  p.z+=(target-p.z)*max(0,1-d/2);v.co=terrain.matrix_world.inverted()@p;changed+=1
 else:v.co=terrain.matrix_world.inverted()@p
# Rock groupings establish natural edge anchors; small stones belong to those groups.
group=collection('VF10_03_Rock_Clusters');rng=random.Random(1010)
stone=material('VF10_Local_Stone',(.18,.20,.185),0,.94)
clusters=[(-46,-61),(-45.8,-55),(-41.5,-50.5),(-31,-65.1),(-28.5,-61.5)]
rock_rows=[]
for k,(cx,cy) in enumerate(clusters):
 for j in range(7):
  x=cx+rng.uniform(-.8,.8);y=cy+rng.uniform(-.8,.8);r=rng.uniform(.32,.65) if j<2 else rng.uniform(.08,.24)
  d=math.hypot(max(-44.6-x,0,x+29.9),max(-64.1-y,0,y+51.9));z=ground(x,y);z+=(-1.34-z)*max(0,1-d/2)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,z+r*.22));o=bpy.context.object;o.name=f'VF10_Rock_{k:02}_{j:02}'
  for c in list(o.users_collection):c.objects.unlink(o)
  group.objects.link(o);o.scale=(r*1.3,r,r*.72);o.rotation_euler=(rng.uniform(-.3,.3),rng.uniform(-.3,.3),rng.uniform(0,6.28))
  for v in o.data.vertices:v.co*=rng.uniform(.86,1.12)
  o.data.materials.append(stone)
  for p in o.data.polygons:p.use_smooth=True
  rock_rows.append({'name':o.name,'location':list(o.location),'radius':r})
stage=collection('VF10_90_Presentation')
camera('VF10_Arrival_View',(-22,-76,14),(-37,-58,-.5),44)
camera('VF10_Parking_Plan',(-37.25,-58.5,27),(-37.25,-58.5,-1),44)
area('VF10_Preview_Key',(-35,-57,12),(-37,-58,-1),2200,12,(1,.9,.77))
s.camera=bpy.data.objects['VF10_Arrival_View'];s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=24
layout={'bounds':[-44.5,-30,-64,-52],'surface_z':-1,'bay_centres':[[-43,-60],[-40,-60],[-37,-60]],'lane_bounds':[-44.5,-30,-57.5,-52],'car_preserved':True,'terrain_vertices_changed':changed,'port_scope':'Parking only. VF08/VF09 service changes remain a separate migration. Reconcile initial forest path surface ownership at the lot exit before Unreal import.'}
layout['rocks']=rock_rows
(OUT/'layout.json').write_text(json.dumps(layout,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Parking_Arrival.blend'))
for name in ['VF10_Arrival_View','VF10_Parking_Plan']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
