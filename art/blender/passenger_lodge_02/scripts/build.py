import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
source=REPO/'art/blender/passenger_lodge_01/Maldek_Passenger_Lodge_Layout.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
ref=bpy.data.scenes['03_Existing_Station_Reference'];s=ref.copy();s.name='04_Combined_Station_Blockout';s.use_fake_user=True;bpy.context.window.scene=s
for n in ['NEW_LODGE_STAGING_ONLY_NOT_SITE_PLACEMENT','STAGING_EXPLANATION']:
 o=bpy.data.objects.get(n)
 if o and o.name in s.collection.objects:s.collection.objects.unlink(o)
def exclude(lc,names):
 if lc.name in names:lc.exclude=True
 for c in lc.children:exclude(c,names)
exclude(s.view_layers[0].layer_collection,{'VF06_Waiting_Hall','VF07_Public_Deck','VF07_Public_Guards','VF07_Deck_Structure'})
c=bpy.data.collections.new('PL02_New_Deck_Rails_and_Stair');s.collection.children.link(c)
ret=bpy.data.collections.new('PL02_Retained_East_Rails_and_Supports');s.collection.children.link(ret)
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
bpy.context.view_layer.update()
kept=[]
for cn in ['VF07_Public_Guards','VF07_Deck_Structure']:
 for o in bpy.data.collections[cn].objects:
  lo,hi=bounds(o)
  if lo[0]>=-8.1001:ret.objects.link(o);kept.append(o.name)
def box(n,x,y,z,w,d,h,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x+w/2,y+d/2,z+h/2));o=bpy.context.object;o.name=n;o.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(mat);return o
plate=bpy.data.materials['Layout_Wet_Tile'];steel=bpy.data.materials['Layout_Petrol_Enamel'];gold=bpy.data.materials['Layout_Brass_Markers']
def beam(n,a,b,r=.035):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(steel)
def rail(n,a,b,z=4):
 for h in [.55,1.1]:beam(n+'_bar',(*a,z+h),(*b,z+h))
 N=max(1,math.ceil(math.dist(a,b)/1.5))
 for i in range(N+1):
  x=a[0]+(b[0]-a[0])*i/N;y=a[1]+(b[1]-a[1])*i/N;beam(n+'_post',(x,y,z),(x,y,z+1.1),.045)
def subtract(r,h):
 x0,x1,y0,y1=r;a,b,e,f=h
 ix0=max(x0,a);ix1=min(x1,b);iy0=max(y0,e);iy1=min(y1,f)
 if ix0>=ix1 or iy0>=iy1:return [r]
 return [q for q in [(x0,ix0,y0,y1),(ix1,x1,y0,y1),(ix0,ix1,y0,iy0),(ix0,ix1,iy1,y1)] if q[1]-q[0]>.001 and q[3]-q[2]>.001]
layout=json.loads((REPO/'art/blender/visual_fidelity_07/layout.json').read_text())
study=(-31.45,-8.1,-15.15,7.35)
floor_rects=[]
for r in layout['deck_rects']:
 for q in subtract(tuple(r[:4]),study):floor_rects.append(q)
new=[study]
holes=[(-10.1,-8.1,-7.7,-5.7),(-24.1,-10.1,-7.2,4),(-24.1,-19.1,-12.2,-7.2),(-16.1,-10.1,-13.2,-7.2),(-19.1,-16.1,-13.2,-7.2)]
for h in holes:new=[p for q in new for p in subtract(q,h)]
floor_rects+=new
for i,(x0,x1,y0,y1) in enumerate(floor_rects):box(f'PL02_Deck_{i:03}',x0,y0,3.8,x1-x0,y1-y0,.2,plate)
inst=bpy.data.objects.new('PL02_Lodge_Fitted',None);inst.instance_type='COLLECTION';inst.instance_collection=bpy.data.collections['PL01_Linked_Lodge_Assembly'];inst.location=(-24.1,4,4);s.collection.objects.link(inst)
inst['status']='Combined blockout proposal; west/north expansion avoids fixed arrival flight. Not an Unreal placement.'
# Real scene objects allow floor/headroom rays to include the lodge, unlike instances.
inst.instance_type='NONE'
placed=bpy.data.collections.new('PL02_Fitted_Lodge_Geometry');s.collection.children.link(placed)
for cn in ['PL01_Shell','PL01_Furniture_Footprints','PL01_Restroom_Fixtures','PL01_Labels_and_Clearances']:
 for original in bpy.data.collections[cn].objects:
  ob=original.copy();ob.data=original.data;ob.name='FIT_'+original.name;placed.objects.link(ob);ob.matrix_world=Matrix.Translation(Vector((-24.1,4,4)))@original.matrix_world
# Retire fittings occupying the replacement envelope, not entire control-side systems.
removed=[];affected=set();blocked=set()
for ob in ref.objects:
 if ob.type!='MESH':continue
 lo,hi=bounds(ob)
 if lo[2]<3.75 or hi[2]>7.36:continue
 if any(lo[0]<h[1]-.02 and hi[0]>h[0]+.02 and lo[1]<h[3]-.02 and hi[1]>h[2]+.02 for h in holes[1:]):
  if any(cc.name.startswith('PL0') for cc in ob.users_collection):continue
  removed.append(ob.name);blocked.add(ob)
  affected.update(cc.name for cc in ob.users_collection if cc.name not in ['VF06_Waiting_Hall','VF07_Public_Deck','VF07_Public_Guards','VF07_Deck_Structure'])
for cn in affected:
 for ob in bpy.data.collections[cn].objects:
  if ob not in blocked and ob.name not in ret.objects:ret.objects.link(ob)
exclude(s.view_layers[0].layer_collection,affected)

print('Lodge and replacement fittings ready',flush=True)
# Deck perimeter: retain the existing arrival opening and reconnect its original landing.
for i,(a,b) in enumerate([
 ((-31.45,-15.15),(-31.45,7.35)),((-31.45,7.35),(-4,7.35)),
 ((-31.45,-15.15),(-23,-15.15)),((-21,-15.15),(-8.1,-15.15)),
 ((-8.1,-15.15),(-8.1,-13.2)),((-8.1,-6.2),(-8.1,-5.5))]):rail(f'PL02_Perimeter_{i}',a,b)
# Structural placeholders stop at source-ground height only where terrain is found.
support=[]
for x in [-30.6,-25.5]:
 for y in [-13.8,-6,1,6.4]:
  hit,loc,normal,idx,obj,m=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,3.6)),Vector((0,0,-1)),distance=40)
  if hit and loc.z<3.5:
   box('PL02_Support',x-.12,y-.12,loc.z,.24,.24,3.8-loc.z,steel);support.append({'xy':[x,y],'ground_z':loc.z,'hit':obj.name})
  else:support.append({'xy':[x,y],'ground_z':None})
# Right-side stair, parallel to bypass. Existing arrival and machinery stairs are retained.
# 24 risers over nominal four metres, with a separate upper turning landing.
for i in range(24):
 y=-14.42+i*.28;z=(i+1)*4/24
 box(f'PL02_Bypass_Stair_{i:02}',-8.1,y,z-.12,1.8,.28,.12,plate)
box('PL02_Bypass_Upper_Landing',-10.1,-7.7,3.8,3.8,2,.2,plate)
box('PL02_Bypass_Lower_Landing',-8.1,-16.22,-.18,1.8,1.8,.18,plate)
for x in [-8.1,-6.3]:
 beam('PL02_Stair_rail',(x,-14.42,1.1),(x,-7.7,5.1));beam('PL02_Stair_midrail',(x,-14.42,.55),(x,-7.7,4.55))
 for i in range(0,24,4):
  y=-14.42+i*.28;z=(i+1)*4/24;beam('PL02_Stair_post',(x,y,z),(x,y,z+1.1))
rail('PL02_Landing_outer',(-6.3,-7.7),(-6.3,-5.7))
exec(compile((OUT/'scripts/refine_edges.py').read_text(), 'refine_edges.py', 'exec'))
print('Deck and stairs ready',flush=True)
routes={

 'Fixed_arrival_turn':next(r['points'] for r in layout['routes'] if r['name']=='Arrival turn onto platform'),
 'Arrival_to_lodge':[[-23.1,-14.3,4],[-17.1,-14.3,4],[-17.1,-6.8,4]],
 'Lodge_to_platform':[[-17.1,-6.8,4],[-17.1,4.2,4],[-17.1,5.5,4],[-4,5.5,4]],
 'Exterior_bypass':[[-17.1,-14.3,4],[-9.1,-14.3,4],[-9.1,2,4],[-5,2,4]],
 'West_promenade':[[-28,-14,4],[-28,5.5,4],[-17.1,5.5,4]]}
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();checks=[]
for n,pts in routes.items():
 failures=[]
 for a,b in zip(pts,pts[1:]):
  N=max(2,math.ceil(math.dist(a,b)/.2))
  for i in range(N+1):
   p=Vector(a).lerp(Vector(b),i/N)
   for dx,dy in [(0,0),(.3,0),(-.3,0),(0,.3),(0,-.3)]:
    hit,loc,_,_,ob,_=s.ray_cast(dg,p+Vector((dx,dy,2.05)),Vector((0,0,-1)),distance=2.5)
    if not hit:
     # Adjacent slab boundary rays can fall on the shared edge; probe a 2 mm patch.
     for ex,ey in [(.002,0),(-.002,0),(0,.002),(0,-.002)]:
      hit,loc,_,_,ob,_=s.ray_cast(dg,p+Vector((dx+ex,dy+ey,2.05)),Vector((0,0,-1)),distance=2.5)
      if hit:break
    if not hit or abs(loc.z-p.z)>.23:failures.append({'p':list(p),'object':ob.name if hit else None,'z':loc.z if hit else None})
 checks.append({'route':n,'failed_samples':len(failures),'examples':failures[:4]})
print('Route checks ready',flush=True)
def camera(n,pos,target,scale):
 cd=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,cd);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=scale;return o
cams=[camera('PL02_Combined_Overview',(-48,-39,36),(-13,-1,3),55),camera('PL02_Combined_Plan',(-12,-1,55),(-12,-1,0),52)]
s.camera=cams[0];s.cycles.samples=16;s.render.resolution_x=1600;s.render.resolution_y=1200
report={'lodge_offset_m':list(inst.location),'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==source_hash,'retired_fittings':removed,'fixed_arrival':'Source stair and path retained; grating requires area-contact rather than isolated vertical rays','protected_anchors':layout['anchors'],'retained_east_objects':len(kept),'routes':checks,'support_probes':support,'stage':'Combined Blender blockout, not final collision or Unreal integration','issues':['Second stair lower tie-in needs terrain/service-yard validation','Deck is solid blockout; grating detailing deferred']}
(OUT/'fit_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
for cam in cams:s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{cam.name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=cams[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
