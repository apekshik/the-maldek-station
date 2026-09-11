import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];A=json.loads((P/'assembly.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Emergency_Power_Fitted.blend'))
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];fs=[list(p.vertices) for p in me.polygons];t=BVHTree.FromPolygons(v,fs,all_triangles=False,epsilon=0);ev.to_mesh_clear();return t
cases={
 'WSE_Door_hinge_S':('WSE_Door_jamb','WSE_Door_header','WSE_Threshold','WS_BaseWest'),
 'WSE_Door_hinge_N':('WSE_Door_jamb','WSE_Door_header','WSE_Threshold','WS_BaseWest'),
 'WSE_Distribution_hinge':('WSE_Distribution_case','WS_BaseEast','WSE_Transfer_box'),
 'WSE_Battery_lid_hinge':('WSE_Battery_case','WSE_Battery.','WSE_Hold_down','WSE_Protected_terminal'),
 'WSE_Engine_cover_hinge':('WSE_Control_box','WSE_Crankcase','WSE_Cylinder_head','WSE_Fuel_isolation_lever')}
results=[]
for name,prefixes in cases.items():
 m=next(q for q in A['mechanisms'] if q['pivot']==name);p=bpy.data.objects[name];static=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefixes)];trees={o.name:tree(o) for o in static};hits=[]
 for k in range(37):
  angle=m['open_degrees']*k/36;p.rotation_euler['XYZ'.index(m['axis'])]=math.radians(angle);bpy.context.view_layer.update()
  for o in p.children:
   if o.type!='MESH':continue
   tr=tree(o)
   for n,t in trees.items():
    if tr.overlap(t):hits.append({'angle':angle,'moving':o.name,'stationary':n})
 p.rotation_euler=(0,0,0);bpy.context.view_layer.update();results.append({'pivot':name,'samples':37,'surface_intersections':hits})
# measured clear opening with both leaves at 90 degrees
for n in ['WSE_Door_hinge_S','WSE_Door_hinge_N']:
 m=next(q for q in A['mechanisms'] if q['pivot']==n);bpy.data.objects[n].rotation_euler[2]=math.radians(m['open_degrees'])
bpy.context.view_layer.update()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
south=bounds(bpy.data.objects['WSE_Service_door']);north=bounds(bpy.data.objects['WSE_Service_door.001']);header=bounds(bpy.data.objects['WSE_Door_header']);threshold=bounds(bpy.data.objects['WSE_Threshold']);width=min(bounds(o)[0][1] for o in bpy.data.objects['WSE_Door_hinge_N'].children if o.type=='MESH')-max(bounds(o)[1][1] for o in bpy.data.objects['WSE_Door_hinge_S'].children if o.type=='MESH');height=min(header[0][2],bounds(bpy.data.objects['WSE_Door_head_seal'])[0][2])-threshold[1][2]
reach={};ops={'WSE_START':(3.85,4.15,1.2),'WSE_TRANSFER':(4.5,5.48,1.2),'WSE_FUEL_ISOLATE':(2.44,4.05,1.2),'WSE_FUEL_CHECK':(2.25,4.05,1.2),'WSE_BATTERY_SERVICE':(4.9,4.15,1.2),'WSE_EMERGENCY_STOP':(2.94,4.15,1.2),'WSE_STATUS_READ':(3.45,4.15,1.2)}
for n,p in ops.items():reach[n]={'operator_hand_local':p,'anchor_distance_m':(Vector(A['anchors'][n])-Vector(p)).length}
r={'method':'Reopened fitted meshes, 37 sampled poses per assembly; evaluated BVH surface intersection against explicitly listed relevant cases/shell. This does not replace engine collision or continuous rigid-body simulation. Hinge barrels/fasteners are excluded intentional hardware contacts.','mechanisms':results,'door_open_width_m':width,'door_headroom_m':height,'reach':reach,'reach_assumption':'0.95 m reach radius from a standing hand at 1.20 m; illustrative gameplay target, not player animation validation.','passed':all(not x['surface_intersections'] for x in results) and width>=1.4 and height>=2.1 and all(x['anchor_distance_m']<=.95 for x in reach.values())};(P/'mechanism_verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

