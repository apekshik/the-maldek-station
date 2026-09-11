import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];FILE=OUT/'Maldek_Station_Furnished.blend'
bpy.ops.wm.open_mainfile(filepath=str(FILE));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
m=json.loads((OUT/'manifest.json').read_text());report={'scope':'Saved/reopened Blender dressing verification; sampled body probes, not Unreal collision.'}
report['source_hash_matches']=hashlib.sha256(Path(m['source']).read_bytes()).hexdigest()==m['source_sha256']
report['changed_existing_transforms']=[n for n,rows in m['preserved_transforms'].items() if n not in s.objects or any(abs(s.objects[n].matrix_world[i][j]-rows[i][j])>1e-5 for i in range(4) for j in range(4))]
report['removed_placeholder_absent']=all(n not in s.objects for n in m['removed'])
report['new_objects']=sum(len(v) for v in m['collections'].values());report['topology_errors']=[];report['new_meshes']=0
for o in s.objects:
 if not o.name.startswith('SD_') or o.type!='MESH':continue
 report['new_meshes']+=1;eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 bad=sum(not e.is_manifold for e in bm.edges)
 if bad or any(f.calc_area()<1e-10 for f in bm.faces):report['topology_errors'].append({'object':o.name,'bad_edges':bad})
 bm.free();eo.to_mesh_clear()
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
 if hi[0]<-41 or lo[0]>-9 or hi[1]<-15 or lo[1]>11 or hi[2]<.5 or lo[2]>7:continue
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
 'Janitor_access':[(-12.4,-7.9,4),(-11.4,-7.9,4)],
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

report['passed']=report['source_hash_matches'] and report['removed_placeholder_absent'] and not report['changed_existing_transforms'] and not report['topology_errors'] and all(r['passed'] for r in report['routes'])
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
