"""Sample complete-width route cross sections, headroom and footsteps on evaluated geometry.
Reports actual blockers. This is mesh-level review, not Unreal capsule validation.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Station_Cleanup.blend'))
s=bpy.context.scene
# Obsolete render-hidden collision/blockout meshes must not mask actual visual obstacles.
for o in bpy.data.objects:
 if o.hide_render:o.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
layout=json.loads((OUT/'layout.json').read_text());results=[];raycount=0
verts=[];tris=[];owners=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(verts)
 verts.extend([o.matrix_world@v.co for v in me.vertices]);tris.extend([tuple(off+i for i in t.vertices) for t in me.loop_triangles]);owners.extend([o.name]*len(me.loop_triangles));ev.to_mesh_clear()
print('BUILD_BVH',len(verts),len(tris),flush=True)
bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
del verts,tris
def hit(a,b):
 global raycount
 raycount+=1;a=Vector(a);b=Vector(b);d=b-a
 if d.length<1e-5:return None
 p,n,idx,dist=bvh.ray_cast(a,d.normalized(),d.length)
 return {'object':owners[idx],'point':[round(v,4) for v in p]} if p is not None else None
def sample_path(points):
 out=[]
 for a,b in zip(points,points[1:]):
  a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/.25))
  for i in range(n):out.append(a+(b-a)*i/n)
 return out+[Vector(points[-1])]
for r in layout['routes']:
 # Stairs already contain one sample per tread; interpolating floor heights would
 # put sample soles inside risers. Horizontal landings/routes are interpolated.
 stair=r['name'] in ['Arrival','Quarters','Exterior_service','Internal descending stair']
 pts=[Vector(p) for p in r['points']] if stair else sample_path(r['points'])
 fail=[];width=r['clear_width'];floor_samples=0
 for i,p in enumerate(pts):
  t=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];t.z=0
  if t.length<1e-5:continue
  side=Vector((-t.y,t.x,0)).normalized();up=Vector((0,0,1))
  for h in [.25,.8,1.4,2.05]:
   a=p-side*(width/2)+up*h;b=p+side*(width/2)+up*h
   obstacle=hit(a,b)
   if obstacle:fail.append({'sample':i,'kind':'width','height':h,**obstacle})
  for f in [-.5,-.25,0,.25,.5]:
   a=p+side*(width*f)+up*.25;obstacle=hit(a,a+up*1.85)
   if obstacle:fail.append({'sample':i,'kind':'headroom','lateral':f,**obstacle})
  # 0.18 m foot patch, sufficient to span several real grating bars.
  contacts=0
  for dx,dy in [(0,0)]+[(i*.017,j*.017) for i in range(-5,6) for j in range(-5,6)]:
   a=p+Vector((dx,dy,.13));floor=hit(a,a-up*.27)
   if floor:contacts+=1;break
  if contacts==0:fail.append({'sample':i,'kind':'floor','point':list(p)})
  floor_samples+=1
 results.append({'name':r['name'],'clear_width_m':width,'samples':len(pts),'pass':not fail,'failures':fail[:35],'failure_count':len(fail)})
 print('ROUTE',r['name'],'samples',len(pts),'failures',len(fail),flush=True)
checks=[]
for name,bb in layout['anchors'].items():
 o=bpy.data.objects[name];p=[o.matrix_world@Vector(v) for v in o.bound_box];now=[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
 err=max(abs(now[i][j]-bb[i][j]) for i in range(2) for j in range(3));checks.append({'name':name,'pass':err<1e-4,'error_m':err})
# No broad opaque mesh behind the new control strip and north perimeter strip.
for name,p in [('Control grating aperture',(-5.53,.732,4)),('West dock grating aperture',(-6.531,6.231,4))]:
 # Render mesh check excludes joists: reports authored tile coverage, not ray aliasing.
 tiles=[r for r in layout['deck_rects'] if r[5]=='grate' and r[0]<=p[0]<=r[1] and r[2]<=p[1]<=r[3] and r[4]==p[2]]
 checks.append({'name':name,'pass':bool(tiles),'covering_grating_rectangles':tiles})
out={'scope':'Evaluated Blender mesh cross-section rays over declared clear route widths; not Unreal movement/collision validation.','ray_count':raycount,'routes':results,'anchor_and_surface_checks':checks,'failed_routes':[r['name'] for r in results if not r['pass']]}
(OUT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'rays':raycount,'failed_routes':out['failed_routes'],'failures':{r['name']:r['failures'][:5] for r in results if not r['pass']}},indent=2))
