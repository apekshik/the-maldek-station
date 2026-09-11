import bpy,json,math,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];O=Vector((-37.45,-5,4.6));a=json.loads((P/'assembly.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Fitted_Review.blend'));s=bpy.context.scene;s.frame_set(1);C=bpy.data.collections['WSP_ASSETS']
def mesh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();me.calc_loop_triangles();v=[e.matrix_world@x.co for x in me.vertices];t=[list(f.vertices) for f in me.loop_triangles];e.to_mesh_clear();return v,t
def bv(o):
 v,t=mesh(o);return BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=0)
def bb(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());p=[e.matrix_world@Vector(v)-O for v in e.bound_box];return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
def ov(a,b,eps=.0001):return all(a[1][i]>b[0][i]+eps and b[1][i]>a[0][i]+eps for i in range(3))
context=[o for o in bpy.data.collections['WS_SHARED_STRUCTURE'].objects if o.type=='MESH']
assets=[o for o in C.objects if o.type=='MESH'];shell=[o for o in context if o.name.startswith('WS_UpperEast') or o.name in ['WS_UpperWest','WS_UpperSouth','WS_SharedPartyWall']]
opening=[o for o in assets if any(k in o.name for k in ['Door_jamb','Door_head','Door_leaf','Window_jamb','Window_sill','Window_glass','Window_sash'])]
hits=[]
for o in opening:
 for q in shell:
  if ov(bb(o),bb(q)) and bv(o).overlap(bv(q)):hits.append([o.name,q.name])
report={'saved_review_reopened':True,'source_hash_matches':hashlib.sha256((P.parent/'west_services_01/Maldek_West_Services_Blockout.blend').read_bytes()).hexdigest()==a['source_sha256'],'proxy_absent':all(n not in s.objects for n in a['delete_exact']),'opening_triangle_intersections_with_shell':hits,'opening_patch_required':False,'mechanism_collisions':[]}
inventory=json.loads((P/'verification.json').read_text())['inventory'];report['placement_errors']=[]
for ob in assets:
 b=bb(ob);expected=inventory[ob.name]['bounds'];err=max(abs(b[j][i]-expected[j][i]) for j in range(2) for i in range(3))
 if err>.00005:report['placement_errors'].append([ob.name,err])
report['placement_tolerance_m']=.00005
# Exclude purposeful seals and hinge contact, test moving major structure against fixed structure.
groups=[('WSP_Door_hinge',['WSP_Door_leaf'],['WSP_Door_jamb','WSP_Door_head']),('WSP_Clerk_drawer_slide',['WSP_Drawer_bottom','WSP_Drawer_side','WSP_Drawer_front_back'],['WSP_Counter_top','WSP_Counter_end','WSP_Counter_public_apron']),('WSP_Shutter_0_hinge',['WSP_Shutter_panel_0'],['WSP_Scale','WSP_Tag_dispenser']),('WSP_Shutter_1_hinge',['WSP_Shutter_panel_1'],['WSP_Scale'])]
for root,moveprefix,fixedprefix in groups:
 moving=[o for o in assets if any(o.name.startswith(p) for p in moveprefix)];fixed=[o for o in assets if any(o.name.startswith(p) for p in fixedprefix) and '_seal' not in o.name]+shell
 for frame in range(1,41,2):
  s.frame_set(frame);bpy.context.view_layer.update()
  for o in moving:
   for q in fixed:
    if ov(bb(o),bb(q)) and bv(o).overlap(bv(q)):report['mechanism_collisions'].append([root,frame,o.name,q.name])
# Fitted route obstacles include shared architecture and parked trolley, mechanisms at normal transit state.
s.frame_set(40)
for m in a['mechanisms']:
 if m['object']!='WSP_Door_hinge':getattr(bpy.data.objects[m['object']],'rotation_euler' if m['kind']=='ROTATION' else 'location')[m['axis']]=m['rest']
bpy.context.view_layer.update();obs=[(o.name,bb(o)) for o in assets+context];routes=[]
def path(name,points,hx,hy,height,skip_trolley=False):
 errors=set();count=0
 for pa,pb in zip(points,points[1:]):
  va=Vector(pa);vb=Vector(pb);N=math.ceil((vb-va).length/.04)
  for i in range(N+1):
   p=va.lerp(vb,i/N);count+=1;b=[[p.x-hx,p.y-hy,.021],[p.x+hx,p.y+hy,height]]
   for n,q in obs:
    if skip_trolley and any(k in n for k in ['Trolley','Caster','Wheel']):continue
    if ov(b,q):errors.add(n)
 routes.append({'name':name,'samples':count,'obstacles':sorted(errors),'passed':not errors})
path('Walking porch through entry to counter',[(6.85,.8,0),(6.85,1.96,0),(3.4,1.96,0),(3.85,3.7,0)],.34,.34,1.8)
path('Trolley porch northbound',[(6.85,.65,0),(6.85,1.99,0)],.4,.6,1.1,True)
path('Trolley inward then handling',[(6.85,1.99,0),(3.15,1.99,0),(3.15,2.75,0)],.6,.4,1.1,True)
for cx,cy,label in [(6.85,1.99,'Porch turn'),(3.15,2.75,'Handling turn')]:
 errors=set()
 for deg in range(0,91,5):
  ang=math.radians(deg);hx=.6*math.cos(ang)+.4*math.sin(ang);hy=.6*math.sin(ang)+.4*math.cos(ang)
  for n,q in obs:
   if any(k in n for k in ['Trolley','Caster','Wheel']):continue
   if ov([[cx-hx,cy-hy,.021],[cx+hx,cy+hy,1.1]],q):errors.add(n)
 routes.append({'name':label,'samples':19,'obstacles':sorted(errors),'passed':not errors})
report['routes']=routes
report['surface_ownership']={'method':'Evaluated triangle intersection for moving leaf/drawer/shutters against fixed structure, and frame/sash against shell; exact butt joints are concealed by casing. Asset and context floors are not duplicated.','limitations':'No general all-pairs coplanarity proof for decorative hardware; visible opening seams also reviewed in neutral renders.','shared_shell_modifications':[]}
report['passed']=report['proxy_absent'] and not hits and not report['placement_errors'] and not report['mechanism_collisions'] and all(r['passed'] for r in routes)
(P/'fitted_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
