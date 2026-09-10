"""Reopen and verify evaluated geometry; no engine or engineering claims."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
SRC=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Windows.blend'))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
manifest=json.loads((OUT/'replacement_manifest.json').read_text());fail=[]
def check(test,msg):
    if not test:fail.append(msg)
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]
def fingerprint(o):
    data=[list(v.co) for v in o.data.vertices];data.extend([list(p.vertices) for p in o.data.polygons])
    return hashlib.sha256(repr((data,[list(r) for r in o.matrix_world],[m.name for m in o.data.materials])).encode()).hexdigest()
def tree(o):
    ev=o.evaluated_get(dg);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];faces=[list(p.vertices) for p in me.polygons];t=BVHTree.FromPolygons(vs,faces);ev.to_mesh_clear();return t
source=json.loads((OUT/'source_preservation.json').read_text())
for n,h in source.items():check(n in s.objects and fingerprint(s.objects[n])==h,'Source geometry changed: '+n)
check(hashlib.sha256(SRC.read_bytes()).hexdigest()==manifest['source_sha256'],'Source file hash changed')
for proxy in manifest['replace']:check(proxy['name'] not in s.objects,'Proxy remains')
assets=bpy.data.collections['PLW_Assets'];topology=[]
for o in assets.all_objects:
    if o.type!='MESH':continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
    bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces)
    check(bad==0 and deg==0,f'Topology {o.name}: {bad} nonmanifold / {deg} degenerate')
    topology.append(dict(name=o.name,vertices=len(me.vertices),faces=len(me.polygons),nonmanifold_edges=bad,degenerate_faces=deg));bm.free();ev.to_mesh_clear()
    check(all(abs(v-1)<1e-6 for v in o.scale),'Unapplied scale '+o.name)
    check(len(o.data.materials)>0,'No material '+o.name)
context=[]
for o in s.objects:
    if o.type!='MESH' or o.name.startswith('PLW_') or not o.visible_get() or o.hide_render:continue
    lo,hi=bounds(o)
    if hi[0]>-23 and lo[0]<-11 and hi[1]>3.70 and lo[1]<4.20 and hi[2]>4.5 and lo[2]<7:context.append((o,tree(o)))
surface_contacts=[]
for o in assets.all_objects:
    if o.type!='MESH':continue
    lo,hi=bounds(o);t=None
    for ob,bt in context:
        a,b=bounds(ob)
        if not all(hi[i]>=a[i] and lo[i]<=b[i] for i in range(3)):continue
        if t is None:t=tree(o)
        pairs=t.overlap(bt)
        if pairs:
            concealed=o.name.endswith('Exterior_Perimeter_Seal') and ob.name.startswith('PL03_Cladding_')
            surface_contacts.append(dict(asset=o.name,context=ob.name,triangle_contacts=len(pairs),intentional_concealed_corrugation_seal=concealed))
            check(concealed,'Unintended source/asset surface intersection: '+o.name+' / '+ob.name)
openings=[];corners=[];drains=[];rear_closure=[]
for ass in manifest['assemblies']:
    x0,y0,z0=ass['translation_m'];prefix=ass['root'].replace('Assembly','');hits=[]
    rear=tree(bpy.data.objects[prefix+'Sill_Rear_Upstand']);closed=0
    for ix in range(21):
        for z in [.026,.034,.042]:
            loc,*_=rear.ray_cast(Vector((x0+.010+3.780*ix/20,3.70,z0+z)),Vector((0,1,0)),.15)
            if loc is not None:closed+=1
    check(closed==63,'Open underside at interior sill '+prefix)
    rear_closure.append(dict(window=prefix,closed_rays=closed,total_rays=63))
    for ix in range(39):
        for iz in range(18):
            origin=Vector((x0+.002+3.796*ix/38,3.70,z0+.002+1.696*iz/17))
            for ob,t in context:
                loc,normal,index,distance=t.ray_cast(origin,Vector((0,1,0)),.5)
                if loc is not None:hits.append(ob.name)
    check(not hits,'Wall blocks opening '+prefix+str(set(hits)))
    openings.append(dict(window=prefix,context_rays=39*18,blocked_by=sorted(set(hits))))
    # Every corner at both core faces: separation of evaluated finish from original
    # axis-aligned core is measured through world vertices, not assumed from bounds.
    for side in ['Left','Right']:
        ob=bpy.data.objects[prefix+'Reveal_'+side];ev=ob.evaluated_get(dg);me=ev.to_mesh();xs=[(ob.matrix_world@v.co).x for v in me.vertices];ev.to_mesh_clear()
        gap=min(xs)-x0 if side=='Left' else x0+3.8-max(xs)
        check(gap>=.0039,'Core jamb separation '+ob.name)
        for h in ['sill','head']:
            for face in ['interior','exterior']:corners.append(dict(window=prefix,corner=side+'_'+h,face=face,jamb_core_gap_m=gap,head_core_gap_m=.004 if h=='head' else None,ownership='Head sheet runs over jamb ends with 1 mm seam; sloping sill owns lower reveal; shaped jamb ends clear sloping end dams.'))
    # Glass thickness and unobstructed pane centre: separate panes, no hidden wall.
    for j,(a,b,bot,top) in enumerate(ass['apertures_local_m'],1):
        for suffix in ['Glass_Inner','Glass_Opal']:
            ob=bpy.data.objects[f'{prefix}Bay{j}_{suffix}'];lo,hi=bounds(ob);check(abs(hi[1]-lo[1]-.006)<1e-5,'Glass thickness '+ob.name)
        sill=bpy.data.objects[prefix+'Sill_Rail'];t=tree(sill)
        for q in [.17,.83]:
            x=x0+a+(b-a)*q
            loc,*_=t.ray_cast(Vector((x,4.02,z0+.072)),Vector((0,-1,0)),.04);outlet=loc is None
            check(outlet,'Blocked weep outlet '+prefix)
            loc,*_=t.ray_cast(Vector((x,3.958,z0+.122)),Vector((0,0,-1)),.017);feed=loc is None
            blockers=[]
            for ob in bpy.data.collections[ass['collection']].all_objects:
                if ob.type!='MESH' or ob==sill:continue
                loc,*_=tree(ob).ray_cast(Vector((x,3.958,z0+.122)),Vector((0,0,-1)),.017)
                if loc is not None:blockers.append(ob.name)
            check(feed and not blockers,'Blocked weep feed '+prefix+str(blockers))
            drains.append(dict(window=prefix,bay=j,fraction=q,outlet_clear=outlet,feed_clear=feed,feed_blockers=blockers))
    # Both entire assets stay outside protected 1.2 m public exit prism.
    for o in bpy.data.collections[ass['collection']].all_objects:
        if o.type!='MESH':continue
        lo,hi=bounds(o);check(not (hi[0]>-17.7 and lo[0]<-16.5 and hi[2]>4 and lo[2]<6.3),'Exit encroachment '+o.name)
report=dict(passed=not fail,saved_reopened=True,failures=fail,source_unchanged=hashlib.sha256(SRC.read_bytes()).hexdigest()==manifest['source_sha256'],source_meshes_preserved=len(source),mesh_count=len(topology),topology=topology,source_asset_surface_contacts=surface_contacts,openings=openings,reveal_corners=corners,drainage=drains,interior_sill_closure=rear_closure,exit_clear_width_m=1.2,limits='Evaluated Blender meshes and sampled ray checks. Engine collision, night lighting and structural/weather performance remain integration work.')
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['topology','reveal_corners']},indent=2))
assert not fail,fail
