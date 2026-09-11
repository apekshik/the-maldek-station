import bpy,bmesh,json,math,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]; O=Vector((-37.45,0,4.6))
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Editable.blend'))
S=bpy.context.scene; C=bpy.data.collections['WSR_ASSETS']
blind=bpy.data.objects['WSR_Privacy_blind_fabric']; blind_rest_ok=abs(blind.dimensions.z-.3)<1e-4 and blind.data.shape_keys.key_blocks['Lowered'].value==0
def bounds(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); p=[ev.matrix_world@Vector(v) for v in ev.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
errors=[]; inv={}; normals={}; duplicate=[]
for o in C.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me)
 bad=sum(not e.is_manifold for e in bm.edges); deg=sum(f.calc_area()<1e-12 for f in bm.faces); volume=bm.calc_volume(signed=True)
 if bad or deg or volume<=0: errors.append({'object':o.name,'nonmanifold':bad,'degenerate':deg,'signed_volume':volume})
 inv[o.name]={'vertices':len(me.vertices),'faces':len(me.polygons),'bounds':bounds(o),'uv_layers':[u.name for u in me.uv_layers]}
 # Same-facing axis-aligned evaluated faces: detect competing visible plane areas.
 for f in me.polygons:
  n=(ev.matrix_world.to_3x3()@f.normal).normalized(); ax=max(range(3),key=lambda i:abs(n[i]))
  if abs(n[ax])<.999999:continue
  pts=[ev.matrix_world@me.vertices[i].co for i in f.vertices]; oth=[i for i in range(3) if i!=ax]
  key=(ax,1 if n[ax]>0 else -1,round(sum(p[ax] for p in pts)/len(pts),5))
  # only truly rectangular faces, not bevel polygons whose AABB can overlap at corners
  lo=[min(p[i] for p in pts) for i in oth]; hi=[max(p[i] for p in pts) for i in oth]
  if len(pts)==4 and abs(f.area-(hi[0]-lo[0])*(hi[1]-lo[1]))<1e-7: normals.setdefault(key,[]).append((o.name,lo,hi))
 bm.free();ev.to_mesh_clear()
for k,fs in normals.items():
 for a,b in itertools.combinations(fs,2):
  if a[0]==b[0]:continue
  overlap=[min(a[2][i],b[2][i])-max(a[1][i],b[1][i]) for i in range(2)]
  if min(overlap)>1e-5: duplicate.append({'a':a[0],'b':b[0],'plane':k,'area':overlap[0]*overlap[1]})
motions={}
for name in json.loads((P/'assembly.json').read_text())['mechanisms']:
 root=bpy.data.objects[name]; children=[o for o in C.objects if o.type=='MESH' and (o==root or o in root.children_recursive)]
 if not children:continue
 axis='XYZ'.index(root['axis']); closed=root['closed_degrees']; opened=root['open_degrees']; allp=[]
 S.frame_set(1); root.animation_data_clear() if False else None
 for i in range(51):
  root.rotation_euler[axis]=math.radians(closed+(opened-closed)*i/50); bpy.context.view_layer.update()
  for o in children:allp.extend(bounds(o))
 motions[name]={'sample_count':51,'swept_local_bounds':[[min(p[i] for p in allp) for i in range(3)],[max(p[i] for p in allp) for i in range(3)]]}
 S.frame_set(1)
(P/'asset_geometry.json').write_text(json.dumps({'objects':inv,'topology_errors':errors,'same_facing_coplanar_candidates':duplicate,'mechanism_sweeps':motions},indent=2))
# Reopen fitted file independently, check exact assembly and geometry along route.
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Fitted_Review.blend')); S=bpy.context.scene; S.frame_set(40); bpy.context.view_layer.update()
C=bpy.data.collections['WSR_ASSETS']; ref=json.loads((P/'reference_inspection.json').read_text()); manifest=json.loads((P/'assembly.json').read_text())
def world_bvh(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]); ev.to_mesh_clear(); return tree
door_swing_hits=[]
fixed=[o for o in S.objects if o.type=='MESH' and (o.name.startswith('WS_UpperEast') or o.name.startswith(('WSR_Door_jamb','WSR_Door_head')))]
fixedtrees={o.name:world_bvh(o) for o in fixed}
for side,sign in [('Active',1),('Passive',-1)]:
 root=bpy.data.objects['WSR_Door_'+side+'_HINGE']; leaf=bpy.data.objects['WSR_Door_'+side+'_leaf']
 for angle in range(0,91,2):
  root.rotation_euler.z=math.radians(sign*angle); bpy.context.view_layer.update(); tr=world_bvh(leaf)
  for n,other in fixedtrees.items():
   if tr.overlap(other):door_swing_hits.append([side,angle,n])
S.frame_set(1); bpy.context.view_layer.update()
closed_gaps=[]; open_hits=[]
for frame in [1,40]:
 S.frame_set(frame); bpy.context.view_layer.update(); dep=bpy.context.evaluated_depsgraph_get()
 for iy in range(31):
  for iz in range(23):
   y=1.30+1.50*iy/30; z=.02+2.15*iz/22
   hit,loc,norm,idx,obj,m=S.ray_cast(dep,O+Vector((6.20,y,z)),Vector((-1,0,0)),distance=.70)
   if frame==1 and not hit:closed_gaps.append([y,z])
   if frame==40 and hit:open_hits.append([y,z,obj.name])
fit=[]
for name,o in ref['objects'].items():
 if name in manifest['delete_exactly'] or o['type']!='MESH':continue
 if name in bpy.data.objects:
  bb=bounds(bpy.data.objects[name]); diff=max(abs(bb[j][i]-o['bounds'][j][i]) for j in range(2) for i in range(3))
  if diff>1e-4:fit.append([name,diff])
st=bpy.data.objects['WSR_Stretcher_ROOT']; obstacles=[]
for o in S.objects:
 if o.type!='MESH' or not o.name.startswith(('WS_','WSR_')):continue
 if o in st.children_recursive:continue
 bb=bounds(o); bb=[[v[i]-O[i] for i in range(3)] for v in bb]
 if bb[1][2]<=.025 or bb[0][2]>=1.8:continue
 if bb[1][0]<.2 or bb[0][0]>8.1 or bb[1][1]<-2 or bb[0][1]>4.9:continue
 obstacles.append((o.name,bb))
def corners(x,y,a,L=2.2,W=.75):
 a=math.radians(a); c,s=math.cos(a),math.sin(a)
 return [[x+u*c-v*s,y+u*s+v*c] for u,v in [(-L/2,-W/2),(-L/2,W/2),(L/2,W/2),(L/2,-W/2)]]
def separation(poly,bb):
 q=[(bb[0][0],bb[0][1]),(bb[0][0],bb[1][1]),(bb[1][0],bb[1][1]),(bb[1][0],bb[0][1])]; axes=[(1,0),(0,1)]
 for i in [0,1]:
  dx=poly[i+1][0]-poly[i][0]; dy=poly[i+1][1]-poly[i][1]; le=math.hypot(dx,dy);axes.append((-dy/le,dx/le))
 gaps=[]
 for ax in axes:
  p=[v[0]*ax[0]+v[1]*ax[1] for v in poly]; r=[v[0]*ax[0]+v[1]*ax[1] for v in q]
  gaps.append(max(min(r)-max(p),min(p)-max(r)))
 return max(gaps)
waypoints=[(7,-1,90),(7,2.05,90),(6.94,2.05,90),(6.94,2.08,60),(6.84,2.19,45),(6.73,2.26,30),(6.70,2.16,20),(6.70,2.05,0),(4.00,2.05,0),(3.80,2.25,0),(3.80,2.25,90)]
samples=[]; hits=[]; minsep=99
for a,b in zip(waypoints,waypoints[1:]):
 count=max(1,math.ceil(math.hypot(a[0]-b[0],a[1]-b[1])/.025),math.ceil(abs(a[2]-b[2])/1))
 for i in range(count+1):
  p=[a[j]+(b[j]-a[j])*i/count for j in range(3)]; poly=corners(*p); samplemin=99
  for n,bb in obstacles:
   if bb[1][2]<.62 or bb[0][2]>1.4:continue
   sep=separation(poly,bb); samplemin=min(samplemin,sep)
   if sep<-.0001:hits.append({'sample':len(samples),'object':n,'penetration_bound':-sep})
  samples.append({'pose':p,'corners_xy':poly,'minimum_separating_axis_gap_m':samplemin});minsep=min(minsep,samplemin)
# Walking cylinder represented by exact circle-v-AABB horizontal checks.
walkways=[(7,-1),(7,2.05),(5.5,2.05),(4.55,2.05),(4.55,3.88),(3.05,3.88),(3.05,2.05),(3.05,3.88),(4.7,3.88)]
walkobstacles=list(obstacles)
for o in st.children_recursive:
 if o.type=='MESH':
  bb=bounds(o); bb=[[v[i]-O[i] for i in range(3)] for v in bb]
  if bb[1][2]>.025 and bb[0][2]<1.8:walkobstacles.append((o.name,bb))
walkhits=[]; wn=0
for a,b in zip(walkways,walkways[1:]):
 N=max(1,math.ceil(math.dist(a,b)/.025))
 for i in range(N+1):
  p=[a[j]+(b[j]-a[j])*i/N for j in range(2)];wn+=1
  for n,bb in walkobstacles:
   dist=math.hypot(max(bb[0][0]-p[0],0,p[0]-bb[1][0]),max(bb[0][1]-p[1],0,p[1]-bb[1][1]))
   if dist<.34-1e-4:walkhits.append({'sample':wn,'object':n})
report={'saved_reopened_asset':True,'saved_reopened_fitted':True,'mesh_count':len(inv),'topology_errors':errors,'same_facing_coplanar_candidates':duplicate,'reference_mesh_bounds_changes':fit,'proxy_absent':all(n not in S.objects for n in manifest['delete_exactly']),'asset_root_translation':list(bpy.data.objects['REVIEW_ONLY_WSR_Assembly'].location),'stretcher':{'envelope_m':[2.2,.75],'vertical_test_m':[.62,1.4],'waypoints':waypoints,'sample_count':len(samples),'minimum_separating_axis_gap_m':minsep,'collisions':hits,'samples':samples},'walking':{'radius':.34,'height':1.8,'waypoints':walkways,'samples':wn,'collisions':walkhits},'limitations':['Blender evaluated AABBs are conservative for cylinders and bevels; stretcher collision uses exact rectangle vs AABB SAT. Samples at <=25mm / 1 degree; not continuous or engine collision.','Unreal import basis/materials, collision, actual capsule and carried stretcher, moving glancing neutral/night/torch reviews remain integration gates.']}
report['passed']=not(errors or duplicate or fit or hits or walkhits) and report['proxy_absent']
report['door_opening']={'clear_test_m':[1.50,2.15],'rays_per_state':713,'closed_uncovered_rays':closed_gaps,'open_obstructions':open_hits,'leaf_vs_wall_frame_swing_intersections':door_swing_hits,'swing_sample_degrees':2}
report['passed']=report['passed'] and not(closed_gaps or open_hits or door_swing_hits)
report['privacy_blind_raised_rest']=blind_rest_ok
report['passed']=report['passed'] and blind_rest_ok
(P/'verification.json').write_text(json.dumps(report,indent=2))
def xy(p):return (70+p[0]*100,620-p[1]*100)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="820" viewBox="0 0 1000 820"><rect width="1000" height="820" fill="#f5f2e8"/><g font-family="Arial" fill="#173e3c"><text x="60" y="38" font-size="25">RESCUE ROOM / STRETCHER HANDLING</text><text x="60" y="65" font-size="15">2.20 × 0.75 m envelope · local metres · north (+Y) up · held-open doors</text></g>']
for n,bb in obstacles:
 if not n.startswith(('WS_UpperEast','WS_UpperWest','WS_UpperNorth','WS_SharedPartyWall','WSR_Cot_pad','WSR_Door_Active_leaf','WSR_Door_Passive_leaf','WSR_Heater_housing','WSR_Blanket_cupboard','WSR_Chair_seat')):continue
 x,y=xy((bb[0][0],bb[1][1])); w=(bb[1][0]-bb[0][0])*100;h=(bb[1][1]-bb[0][1])*100
 svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#b8b5a8" stroke="#878477" stroke-width=".6"/>')
svg.append('<polyline fill="none" stroke="#ba602b" stroke-width="3" points="'+' '.join(f'{xy(s["pose"])[0]:.1f},{xy(s["pose"])[1]:.1f}' for s in samples)+'"/>')
for i,p in enumerate(waypoints):
 pts=corners(*p); textpts=' '.join(f'{xy(q)[0]:.1f},{xy(q)[1]:.1f}' for q in pts); x,y=xy(p)
 svg.append(f'<polygon points="{textpts}" fill="#da8b41" fill-opacity=".055" stroke="#aa5628" stroke-width="1.1"/><circle cx="{x}" cy="{y}" r="3" fill="#173e3c"/><text x="{x+5}" y="{y-5}" font-family="Arial" font-size="12">{i+1}</text>')
svg.extend(['<g font-family="Arial" fill="#173e3c" font-size="15"><text x="90" y="745">Sample spacing ≤25 mm / 1° · conservative mesh bounds · not engine collision</text>',f'<text x="90" y="772">{len(samples)} poses · minimum separating-axis margin {minsep*1000:.1f} mm · see verification.json for every corner</text></g></svg>'])
(P/'handling_plan.svg').write_text(''.join(svg),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['stretcher','walking']},indent=2)); print('STRETCHER',len(samples),len(hits),'MIN GAP',minsep,'WALK',len(walkhits));print('FIRST HITS',hits[:12],walkhits[:12])




