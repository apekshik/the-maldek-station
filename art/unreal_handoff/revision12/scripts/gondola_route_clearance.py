import bpy,json,math,bisect
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';plan=json.loads((out/'plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Route_Installed_Variants.blend'),load_ui=False);deps=bpy.context.evaluated_depsgraph_get()
def data(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return v,f
points=plan['rope_samples_m'];ys=[p[1] for p in points]
def rope(y):
 i=max(0,min(len(points)-2,bisect.bisect_right(ys,y)-1));a,c=points[i:i+2];return a[2]+(y-a[1])*(c[2]-a[2])/(c[1]-a[1])
w=12*9.81;H=250000;edge=3.7;ca=(w*300/(2*H))/(2*edge);d=7-edge;stagesag=-ca*edge*edge-w*d*(300-d)/(2*H)
cache=[]
for o in bpy.data.objects:
 if o.name.startswith('STUDY_CABIN_') and 'hanger_adapter' not in o.name and o.type in {'MESH','CURVE','FONT'}:
  vs,fs=data(o);cache.append((o.name,[v+Vector((.15,7,-37.4-stagesag)) for v in vs],fs,True))
vs,fs=data(bpy.data.objects['SM_Gondola_Hanger_Adapter']);cache.append(('new_adapter',[v+Vector((.25,0,0)) for v in vs],fs,False))
fail=[];poses=0
for i,n in enumerate(plan['nodes'][1:-1],1):
 vs,fs=data(bpy.data.objects['SM_Gondola_Pylon_%02d'%i]);pt=BVHTree.FromPolygons(vs,fs,all_triangles=True);tower_vs=vs;tower_fs=fs
 for dy in [-6+j*.25 for j in range(49)]:
  floor=rope(n['y']+dy)-n['ground']-plan['rope_offset_m'];pivot=Vector((.25,dy+.05,floor+3.96))
  for angle in [-8,0,8]:
   poses+=1;rot=Matrix.Rotation(math.radians(angle),3,'Y')
   for name,vs,fs,swing in cache:
    shifted=[v+Vector((0,dy,floor)) for v in vs]
    if swing:shifted=[pivot+rot@(v-pivot) for v in shifted]
    ct=BVHTree.FromPolygons(shifted,fs,all_triangles=True);hits=pt.overlap(ct)
    if hits:fail.append({'pylon':i,'dy':dy,'swing':angle,'part':name,'pairs':len(hits),'contact':list(sum((tower_vs[k] for k in tower_fs[hits[0][0]]),Vector())/3)})
report={'poses':poses,'collisions':fail,'body_swing_degrees':[-8,0,8],'travel_step_m':.25,'tower_count':5,'scope':'Sampled triangle intersections; not a continuous dynamic or capacity check.'}
(out/'clearance.json').write_text(json.dumps(report,indent=2));print('CLEARANCE',poses,'FAILURES',len(fail))
