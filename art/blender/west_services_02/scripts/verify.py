import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];FILE=OUT/'Maldek_Station_West_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(FILE));s=bpy.data.scenes['Station_West_Services_Integrated'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
m=json.loads((OUT/'reconciliation.json').read_text());report={'scope':'Saved/reopened Blender blockout; sampled geometry checks, not Unreal capsule or finished asset verification.'}
changed=[]
for n,rows in m['preserved_context_transforms'].items():
 o=s.objects.get(n)
 if not o or any(abs(o.matrix_world[i][j]-rows[i][j])>1e-5 for i in range(4) for j in range(4)):changed.append(n)
report['context_transform_changes']=changed
report['retired_context_absent']=all(n not in s.objects for n in m['retired_objects'])
report['source_hash_matches']=hashlib.sha256(Path(m['source']).read_bytes()).hexdigest()==m['source_sha256']
mesh_errors=[];meshes=0
for o in s.objects:
 if not o.name.startswith(('WS_','WS02_','WSP_','WSR_','WSE_')) or o.type!='MESH':continue
 meshes+=1;bm=bmesh.new();eo=o.evaluated_get(dg);em=eo.to_mesh();bm.from_mesh(em)
 bad=sum(not e.is_manifold for e in bm.edges)
 if bad or any(f.calc_area()<1e-10 for f in bm.faces):mesh_errors.append({'object':o.name,'nonmanifold_edges':bad})
 bm.free();eo.to_mesh_clear()
report['new_meshes']=meshes;report['topology_errors']=mesh_errors
# Verify exact package placement and immutable asset files at rest, before opening for routes.
report['package_errors']=[];report['package_counts']={}
for p in m['packages']:
 report['package_counts'][p['collection']]=len(bpy.data.collections[p['collection']].all_objects)
 if hashlib.sha256((OUT.parent/p['package']/p['file']).read_bytes()).hexdigest()!=p['sha256']:report['package_errors'].append([p['package'],'source hash changed'])
 for name,data in p['objects'].items():
  ob=s.objects.get(name)
  if not ob:report['package_errors'].append([name,'missing']);continue
  if any(abs(ob.matrix_world[i][j]-data['world_matrix'][i][j])>2e-5 for i in range(4) for j in range(4)):report['package_errors'].append([name,'rest transform'])
  if hasattr(ob.data,'materials') and [mm.name if mm else None for mm in ob.data.materials]!=data['material_slots']:report['package_errors'].append([name,'material slots'])
report['sleeve_patch_present']=bool(s.objects['WS_BaseSouth'].get('WSE_sleeve_patch'))
s.frame_set(40)
# Transit state: public doors open, stored parcel trays and cabinet closed.
pa=json.loads((OUT.parent/'west_services_parcels_01/assembly.json').read_text())
for me in pa['mechanisms']:
 if me['object']=='WSP_Secure_door_hinge' or me['object'].startswith('WSP_Secure_tray'):
  ob=bpy.data.objects[me['object']]
  if ob.animation_data:ob.animation_data_clear()
  getattr(ob,'rotation_euler' if me['kind']=='ROTATION' else 'location')[me['axis']]=me['rest']
pa=json.loads((OUT.parent/'west_services_power_01/assembly.json').read_text())
for me in pa['mechanisms']:
 if me['pivot'].startswith('WSE_Door_hinge'):bpy.data.objects[me['pivot']].rotation_euler['XYZ'.index(me['axis'])]=math.radians(me['open_degrees'])
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()

# Build one immutable evaluated BVH for the route region; avoid repeated full-scene queries.
from mathutils.bvhtree import BVHTree
verts=[];faces=[];owners=[]
for ob in s.objects:
 if ob.type!='MESH' or not ob.visible_get():continue
 bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)]
 if hi[0]<-41 or lo[0]>-27 or hi[1]<-15 or lo[1]>11 or hi[2]<.5 or lo[2]>7:continue
 eo=ob.evaluated_get(dg);me=eo.to_mesh();offset=len(verts)
 verts.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:faces.append(tuple(offset+j for j in f.vertices));owners.append(ob)
 eo.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
def cast(origin,direction,distance):
 loc,normal,index,dist=bvh.ray_cast(origin,direction,distance)
 if index is None:return False,None,None,None,None,None
 return True,loc,normal,index,owners[index],None
print('BVH READY',len(verts),len(faces),flush=True)
# Sample actual supporting surface followed by radial body probes against saved scene.
paths={
 'West_promendade_preserved':[(-28,-14,4),(-28,6.5,4)],
 'Ramp_to_parcels':[(-28,-13.2,4),(-30.45,-13.2,4),(-30.45,-12.2,4),(-30.45,-5,4.6),(-30.45,-3.15,4.6),(-34,-3.15,4.6)],
 'North_steps_to_rescue':[(-28,6.7,4),(-30.45,6.7,4),(-30.45,5,4.6),(-30.45,2.05,4.6),(-32.9,2.05,4.6),(-32.9,3.88,4.6),(-34.4,3.88,4.6)],
 'Porch_between_rooms':[(-30.45,-3.15,4.6),(-30.45,2.05,4.6)],
 'Lower_service':[(-28,6.7,4),(-30.45,6.7,4),(-30.45,7.2,4),(-31.45,7.2,4),(-37.05,7.2,1.2),(-39.3,7.2,1.2),(-39.3,2.2,1.2),(-34,2.2,1.2),(-32.8,2.2,1.2)],
 'Lower_full_wrap':[(-39.3,2.2,1.2),(-39.3,-6.6,1.2),(-30,-6.6,1.2),(-30,9.4,1.2),(-39.3,9.4,1.2),(-39.3,2.2,1.2)]}
report['support_method']='Point ray, with 160 x 120 mm footprint search for open grating matching lodge source verification.';report['routes']=[]
for name,pts in paths.items():
 errs=[];Ntotal=0
 for a,b in zip(pts,pts[1:]):
  N=max(1,math.ceil(math.dist(a,b)/.18))
  for i in range(N+1):
   p=Vector(a).lerp(Vector(b),i/N);Ntotal+=1
   hit,loc,n,idx,ob,mat=cast(p+Vector((0,0,.31)),Vector((0,0,-1)),distance=.7)
   if not hit or abs(loc.z-p.z)>.31:
    # Existing open grating needs a foot-sized support search, not a point ray through a hole.
    found=False
    for dx in [j*.005 for j in range(-16,17)]:
     for dy in [-.06,0,.06]:
      hh,ll,nn,ii,oo,mm=cast(p+Vector((dx,dy,.31)),Vector((0,0,-1)),distance=.7)
      if hh and abs(ll.z-p.z)<.07:
       found=True;loc=ll;break
     if found:break
    if not found:errs.append({'point':list(p),'issue':'support'});continue
   z=loc.z
   # Cylinder-like sampled body envelope; clearance from stair risers at lowest probe.
   for h in [.36,1.0,1.7]:
    for k in range(12):
     direction=Vector((math.cos(k*math.tau/12),math.sin(k*math.tau/12),0))
     hit,q,nn,ii,oo,mm=cast(Vector((p.x,p.y,z+h)),direction,distance=.34)
     if hit:errs.append({'point':list(p),'issue':'body','object':oo.name});break
   hit,q,nn,ii,oo,mm=cast(Vector((p.x,p.y,z+.35)),Vector((0,0,1)),distance=1.45)
   if hit:errs.append({'point':list(p),'issue':'headroom','object':oo.name})
 report['routes'].append({'name':name,'samples':Ntotal,'passed':not errs,'errors':errs[:20],'error_count':len(errs)})
report['openings']=[{'name':'Parcels','rough_width':1.5,'rough_height':2.35},{'name':'Rescue','rough_width':1.7,'rough_height':2.35},{'name':'Power','rough_width':1.6,'rough_height':2.3}]
report['limitations']=['Finished package door/handling tests retained; combined transit pose checked here.','Radial probes approximate walking body; not continuous collision or an engine capsule.','Inherited terrain only; no current Unreal terrain survey.','Shared finish and wrap platform authored; engine export, material baking and collision remain.']
report['passed']=not report['package_errors'] and report['sleeve_patch_present'] and not changed and not mesh_errors and report['source_hash_matches'] and report['retired_context_absent'] and all(r['passed'] for r in report['routes'])
(OUT/'verification.json').write_text(json.dumps(report,indent=2));(OUT/'delivery.json').write_text(json.dumps({'blend':FILE.name,'sha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),'verification_passed':report['passed']},indent=2))
print(json.dumps(report,indent=2),flush=True)



