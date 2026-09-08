import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Tapered_Central_Pylon.blend'),load_ui=False)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
parts=list(bpy.data.collections['PYLON | export geometry'].objects)
assert len([o for o in parts if o.name.startswith('Rubber_sheave')])==12
assert len([o for o in parts if o.name.startswith('Head_longitudinal_carrier')])==1
assert not any(o.name.startswith(('Upper_transverse_tie','Cantilever_mount')) for o in parts)
def meshdata(o,dy=0):
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co+Vector((0,dy,0)) for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return vs,fs
pv=[];pf=[];owners=[]
for o in parts:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 v,f=meshdata(o);k=len(pv);pv+=v;pf += [tuple(k+i for i in tri) for tri in f];owners += [o.name]*len(f)
pt=BVHTree.FromPolygons(pv,pf,all_triangles=True)
cabin=[o for o in bpy.data.objects if o.name.startswith('STUDY_CABIN_') and o.type in {'MESH','CURVE','FONT'} and not o.hide_render]
collisions=[]
travel=[-6+i*.25 for i in range(49)]
angles=[-8,0,8]
w=12*9.81;H=250000.;span=300.;edge=3.7;ca=(w*span/(2*H))/(2*edge)
def rope_z(y):
 u=abs(y)
 if u<=edge:return 42.327-ca*u*u
 d=u-edge;return 42.327-ca*edge*edge-w*d*(span-d)/(2*H)
cache={o:meshdata(o) for o in cabin}
for position in travel:
 dy=position+7;dz=rope_z(position)-rope_z(-7)
 pivot=Vector((.1,position,41.36+rope_z(position)-42.327))
 for angle in angles:
  rot=Matrix.Rotation(math.radians(angle),3,'Y')
  for o in cabin:
   vs,fs=cache[o]
   if not fs:continue
   shifted=[v+Vector((0,dy,dz)) for v in vs]
   if 'hanger_adapter' not in o.name:shifted=[pivot+rot@(v-pivot) for v in shifted]
   ct=BVHTree.FromPolygons(shifted,fs,all_triangles=True)
   overlap=pt.overlap(ct)
   if overlap:collisions.append({'cabin':o.name,'travel_y':position,'swing_deg':angle,'pylon_parts':sorted(set(owners[a] for a,b in overlap)),'triangle_pairs':len(overlap)})
report={'passenger_lanes':1,'main_sheaves':12,'bare_return_rollers':4,'tested_cabin_travel_positions_m':travel,'illustrative_body_swing_degrees':angles,'poses_checked':len(travel)*len(angles),'collisions':collisions,'tower_bounds_m':[[min(p[i] for p in pv) for i in range(3)],[max(p[i] for p in pv) for i in range(3)]],'pylon_triangles':len(pf),'cabin_reference_objects':len(cabin),'production_gondola_modified':False,'runtime_validation':'Pending Unreal terrain, spline and rig integration'}
(out/'clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
