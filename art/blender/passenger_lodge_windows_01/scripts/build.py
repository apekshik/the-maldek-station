"""Run with Blender 5.0 --background --python <this file>. Source stays read-only."""
import bpy, bmesh, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1]
SRC=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
EXPECTED='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
PROXIES=['FIT_Frosted_window_placeholder','FIT_Frosted_window_placeholder.001']
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def fingerprint(o):
    data=[list(v.co) for v in o.data.vertices]
    data.extend([list(p.vertices) for p in o.data.polygons])
    return hashlib.sha256(repr((data,[list(r) for r in o.matrix_world],[m.name for m in o.data.materials])).encode()).hexdigest()
assert digest(SRC)==EXPECTED,'Source changed: survey before authoring.'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
source_records={o.name:fingerprint(o) for o in s.objects if o.type=='MESH' and o.name not in PROXIES}
excluded=set()
def get_excluded(lc):
    if lc.exclude:excluded.add(lc.name)
    for child in lc.children:get_excluded(child)
get_excluded(s.view_layers[0].layer_collection)
def collection(n,parent=None):
    c=bpy.data.collections.new(n);(parent or s.collection).children.link(c);return c
ref=collection('PLW_REFERENCE_ONLY__DO_NOT_EXPORT');ref['export']=False
for c in list(s.collection.children):
    if c!=ref:ref.children.link(c);s.collection.children.unlink(c)
for o in list(s.collection.objects):ref.objects.link(o);s.collection.objects.unlink(o)
def restore(lc):
    if lc.name in excluded:lc.exclude=True
    for child in lc.children:restore(child)
restore(s.view_layers[0].layer_collection)
assets=collection('PLW_Assets');assets['export']=True
review=collection('PLW_REVIEW_ONLY__DO_NOT_EXPORT');review['export']=False
blue=bpy.data.materials['VF06_Petrol_paint'];zinc=bpy.data.materials['VF06_Galvanized'];cream=bpy.data.materials['VF06_Warm_enamel']
def mat(n,color,metal=0,rough=.5):
    m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
rubber=mat('PLW_EPDM_Charcoal',(.016,.021,.020),0,.76)
glass=bpy.data.materials['PL03_Frosted_Glass'].copy();glass.name='PLW_Opal_Glass_6mm'
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.72,.80,.77,1);p.inputs['Roughness'].default_value=.38;p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.52
clear=mat('PLW_Clear_Glass_6mm',(.9,.96,.94),0,.08);p=clear.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.52
spacer=mat('PLW_IGU_Edge_Seal',(.029,.034,.032),0,.62)
roots=[];active=None;root=None;prefix=''
def mesh(n,v,f,m,bevel=0):
    d=bpy.data.meshes.new(prefix+n);d.from_pydata(v,[],f);d.update()
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
    o=bpy.data.objects.new(prefix+n,d);active.objects.link(o);o.parent=root;d.materials.append(m)
    # Local component origins at geometry centre, under the surveyed assembly origin.
    center=sum((v.co for v in d.vertices),Vector())/len(d.vertices)
    for vertex in d.vertices:vertex.co-=center
    o.location=center
    if bevel:
        b=o.modifiers.new('Small manufactured edge radius','BEVEL');b.width=bevel;b.segments=2
    o['surface_owner']=n;o['export']=True
    return o
def box(n,x,y,z,w,d,h,m,bev=.0005):
    v=[(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z),(x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h)]
    return mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,bev)
def extrusion(n,section,axis,start,end,m,bevel=.0005):
    ids=[i for i in range(3) if i!=axis];v=[]
    for t in [start,end]:
        for a,b in section:
            p=[0,0,0];p[axis]=t;p[ids[0]]=a;p[ids[1]]=b;v.append(p)
    N=len(section);f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh(n,v,f,m,bevel)
def ring(n,a,b,z0,z1,y0,y1,t,m,bev=.0004):
    # Continuous mitred rectangular ring, with no internal overlapping corner boxes.
    outer=[(a,z0),(b,z0),(b,z1),(a,z1)];inner=[(a+t,z0+t),(b-t,z0+t),(b-t,z1-t),(a+t,z1-t)]
    v=[(x,y,z) for y in [y0,y1] for loop in [outer,inner] for x,z in loop];f=[]
    for i in range(4):
        j=(i+1)%4
        f.extend([(i,j,j+4,i+4),(i+8,i+12,j+12,j+8),(i,i+8,j+8,j),(i+4,j+4,j+12,i+12)])
    return mesh(n,v,f,m,bev)
def tube(n,x,y,z,w,d,h,axis,m):
    # Rectangular closed-section metal extrusion, 3 mm walls and open bore at ends.
    lo=[x,y,z];hi=[x+w,y+d,z+h];ids=[i for i in range(3) if i!=axis];a,b=ids
    loops=[]
    for inset in [0,.003]:loops.append([(lo[a]+inset,lo[b]+inset),(hi[a]-inset,lo[b]+inset),(hi[a]-inset,hi[b]-inset),(lo[a]+inset,hi[b]-inset)])
    v=[]
    for q in [lo[axis],hi[axis]]:
        for loop in loops:
            for u,t in loop:
                p=[0,0,0];p[axis]=q;p[a]=u;p[b]=t;v.append(p)
    f=[]
    for i in range(4):
        j=(i+1)%4;f.extend([(i,j,j+4,i+4),(i+8,i+12,j+12,j+8),(i,i+8,j+8,j),(i+4,j+4,j+12,i+12)])
    return mesh(n,v,f,m,.0007)
def cut(o,cutter):
    bpy.context.view_layer.update();bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Machined drainage outlet','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def screw(n,x,y,z):
    # Slotted low dome fastener, axis Y; the slot is actual recessed geometry.
    N=16;v=[]
    for r,dy in [(.0033,0),(.0033,-.0011),(.0027,-.0018)]:
        v.extend([(x+r*math.cos(i*math.tau/N),y+dy,z+r*math.sin(i*math.tau/N)) for i in range(N)])
    f=[tuple(reversed(range(N))),tuple(range(2*N,3*N))]
    for k in range(2):f.extend([(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for i in range(N)])
    o=mesh(n,v,f,zinc,0);c=box(n+'_slot_tool',x-.0026,y-.003,z-.00045,.0052,.002,.0009,zinc,0);cut(o,c)
    return o
survey=[];assemblies=[]
for k,name in enumerate(PROXIES):
    proxy=bpy.data.objects[name];lo,hi=bounds(proxy);survey.append(dict(name=name,bounds=[lo,hi]))
    assert abs(hi[0]-lo[0]-3.8)<.00001 and abs(hi[2]-lo[2]-1.7)<.00001
    x0=round(lo[0],4);z0=round(lo[2],4);active=collection(f'PLW_Window_{k+1:02}',assets);prefix=f'PLW_{k+1:02}_'
    root=bpy.data.objects.new(prefix+'Assembly',None);active.objects.link(root);root.location=(x0,4,z0);root.empty_display_size=.2;roots.append(root)
    root['opening_m']=[3.8,.18,1.7];root['fixed_glazing']=True;root['assembly_origin']='West rough jamb / exterior core face / rough sill';root['source_proxy']=name
    # Metal reveals: 4 mm concealed core gap, 2 mm sheet. Head owns top corners.
    for side,x in [('Left',.004),('Right',3.794)]:
        extrusion('Reveal_'+side,[(-.198,.070),(.044,.047),(.044,1.693),(-.198,1.693)],0,x,x+.002,cream,.0002)
    box('Reveal_Head',.004,-.198,1.694,3.792,.242,.002,cream,.0002)
    # Sheet sill slopes outward 30 mm / 316 mm (5.42 degrees), folded down clear of facade.
    extrusion('Sill_Pan', [(-.196,.045),(.120,.015),(.120,-.022),(.118,-.022),(.118,.0128),(-.196,.043)],0,.007,3.793,zinc,.0002)
    for a in [.006,3.792]:
        extrusion('Sill_End_Dam_'+str(a),[(-.196,.046),(.120,.016),(.120,.038),(-.196,.068)],0,a,a+.002,zinc,.0002)
    box('Sill_Rear_Upstand',.008,-.198,.012,3.784,.002,.050,zinc,.0002)
    # Cover core/liner seams with metal returns outside the rough opening plane.
    ring('Interior_Architrave',-.032,3.832,-.016,1.732,-.201,-.1985,.040,cream)
    ring('Exterior_Architrave',-.035,3.835,-.022,1.735,.037,.041,.045,cream)
    # Filled corrugation-to-trim joint occupies its own concealed volume.
    ring('Exterior_Perimeter_Seal',-.032,3.832,-.019,1.732,.030,.0368,.032,rubber,0)
    # Folded head hood: separate weathering surface beyond the cladding peaks.
    extrusion('Head_Drip',[ (.043,1.747),(.098,1.739),(.098,1.720),(.096,1.720),(.096,1.737),(.043,1.745)],0,-.041,3.841,zinc,.0002)
    # Packing/weather seals bridge installation gap; frames remain inside rough hole.
    ring('Installation_Seal',.006,3.794,.044,1.694,-.112,.005,.015,rubber,.0002)
    # Rear bedding closes the frame-to-pan joint; discrete shims carry the sill.
    def pan_top(y):return .045-(y+.196)*.030/.316
    extrusion('Sill_Rear_Bedding',[(-.110,pan_top(-.110)-.0003),(-.090,pan_top(-.090)-.0003),(-.090,.0505),(-.110,.0505)],0,.020,3.780,rubber,.0001)
    for j,x in enumerate([.055,1.285,2.515,3.745]):
        extrusion(f'Sill_Support_Packer_{j+1}',[(-.085,pan_top(-.085)),(-.012,pan_top(-.012)),(-.012,.049),(-.085,.049)],0,x-.023,x+.023,rubber,.0001)
    tube('Jamb_Left',.020,-.108,.049,.070,.110,1.630,2,blue)
    tube('Jamb_Right',3.710,-.108,.049,.070,.110,1.630,2,blue)
    tube('Head',.0905,-.108,1.609,3.619,.110,.070,0,blue)
    sill=tube('Sill_Rail',.0905,-.108,.049,3.619,.110,.070,0,blue)
    inner=3.620;mw=.060;bay=(inner-2*mw)/3
    aperture=[]
    for j in range(3):
        a=.090+j*(bay+mw);b=a+bay;bottom=.119;top=1.609
        aperture.append([a,b,bottom,top])
        if j<2:tube(f'Mullion_{j+1}',b,-.108,.1195,.060,.110,1.489,2,blue)
        # 6 / 12 / 6 mm IGU; 4 mm edge clearance, spacer recessed 3 mm from glass edge.
        box(f'Bay{j+1}_Glass_Inner',a+.004,-.057,bottom+.004,b-a-.008,.006,top-bottom-.008,clear,.00025)
        box(f'Bay{j+1}_Glass_Opal',a+.004,-.039,bottom+.004,b-a-.008,.006,top-bottom-.008,glass,.00025)
        ring(f'Bay{j+1}_IGU_Spacer',a+.007,b-.007,bottom+.007,top-.007,-.051,-.039,.007,zinc,.0001)
        ring(f'Bay{j+1}_IGU_Edge_Seal',a+.004,b-.004,bottom+.004,top-.004,-.051,-.039,.003,spacer,0)
        for side,y0,y1,gy0,gy1 in [('Interior',-.080,-.061,-.061,-.0568),('Exterior',-.029,-.010,-.0332,-.029)]:
            ring(f'Bay{j+1}_{side}_Bead',a-.009,b+.009,bottom-.009,top+.009,y0,y1,.024,blue,.0007)
            ring(f'Bay{j+1}_{side}_EPDM',a-.002,b+.002,bottom-.002,top+.002,gy0,gy1,.022,rubber,.0004)
        for q in [.25,.75]:
            x=a+bay*q
            box(f'Bay{j+1}_Setting_Block_{q}',x-.045,-.058,bottom+.0003,.09,.026,.0037,rubber,.0001)
            screw(f'Bay{j+1}_Bead_Fixing_L_{q}',a+.003,-.080,bottom+(top-bottom)*q)
            screw(f'Bay{j+1}_Bead_Fixing_R_{q}',b-.003,-.080,bottom+(top-bottom)*q)
        # Keep feed mouths away from quarter-point glass support blocks.
        for q in [.17,.83]:
            x=a+bay*q
            tool=box('Weep_Tool',x-.012,-.007,.068,.024,.014,.008,blue,0);cut(sill,tool)
            tool=box('Feed_Tool',x-.012,-.047,.110,.024,.011,.02,blue,0);cut(sill,tool)
    # Neutral assembly ID plate, with no invented safety certification.
    box('ID_Plate',.16,-.110,.069,.10,.0015,.022,zinc,.0003)
    bpy.data.objects.remove(proxy,do_unlink=True)
    bpy.context.view_layer.update()
    assemblies.append(dict(collection=active.name,root=root.name,translation_m=list(root.location),rotation_degrees=[0,0,0],scale=[1,1,1],rough_opening_m=[3.8,1.7],frame_outer_m=[3.76,1.63,.11],frame_wall_m=.003,mullion_face_m=.060,glass_build_up_mm=[6,12,6],apertures_local_m=aperture,moving_parts=[],pivots='Fixed; no moving parts',sill_slope_degrees=math.degrees(math.atan(.030/.316))))

bpy.context.view_layer.update()
objects=[]
for o in assets.all_objects:
    if o.type=='MESH':objects.append(dict(name=o.name,parent=o.parent.name,local_origin_m=list(o.location),world_bounds_m=bounds(o),material_slots=[m.name for m in o.data.materials]))
materials=[]
for m in {m for o in assets.all_objects if o.type=='MESH' for m in o.data.materials}:
    p=m.node_tree.nodes.get('Principled BSDF')
    materials.append(dict(name=m.name,procedural_blender_only=any(n.type in {'TEX_NOISE','TEX_VORONOI','TEX_WAVE','BUMP'} for n in m.node_tree.nodes),base_color=list(p.inputs['Base Color'].default_value) if p else None,roughness=p.inputs['Roughness'].default_value if p else None,transmission=p.inputs['Transmission Weight'].default_value if p else None))
manifest=dict(source=str(SRC.relative_to(OUT.parents[2])),source_sha256=EXPECTED,working_scene=s.name,units='metres; Blender Z up, +Y exterior',replace=survey,asset_collection=assets.name,exclude_from_exports=[ref.name,review.name],assemblies=assemblies,objects=objects,materials=materials,wall_patch=dict(required=False,objects_modified=[],reason='Source openings pass through all visible core/cladding layers. New liners retain 4 mm minimum core setback; returns cover boundary seams. Do not recut the master wall.'),preserved_public_exit=dict(x_range=[-17.7,-16.5],z_range=[4,6.3],width_m=1.2),integration_limits=['No Unreal import/collision/PIE validation','No operable hardware','Custom visual construction; not a rated or engineered manufacturer assembly','Bake procedural station finishes; author LOD/collision and export transforms during integration'])
(OUT/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'source_preservation.json').write_text(json.dumps(source_records,indent=2))
# Keep context visible but distinguish every reference root from delivery geometry.
s['PLW_notes']='Export PLW_Assets only. Reference and review collections are not delivery geometry.'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
def cam(n,pos,target,lens=35,ortho=None):
    d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);review.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.02
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    return o
views=[('PLW_01_Exterior',(-21.4,7.10,5.65),(-20.8,3.97,5.73),26,None),('PLW_02_Exterior',(-13.0,7.1,5.65),(-13.6,3.97,5.73),26,None),('PLW_01_Interior',(-20.4,.80,5.65),(-20.8,3.95,5.70),26,None),('PLW_02_Interior',(-14.0,.8,5.65),(-13.6,3.95,5.70),26,None),('PLW_Facade_Beside_Control',(-32,24,16),(-12,-2,5),35,37),('PLW_Sill_Detail',(-21.6,4.85,5.12),(-21.35,3.98,4.99),48,None),('PLW_Head_Detail',(-22.0,4.65,6.45),(-22.65,4.0,6.56),48,None)]
for n,pos,target,lens,ortho in views:cam(n,pos,target,lens,ortho)
for n in ['PLW_01_Exterior','PLW_02_Exterior']:bpy.data.objects[n].data.lens=24
for i,(pos,target,power,size) in enumerate([((-20,6.3,7.5),(-20,3.9,5.6),650,5),((-13,6.3,7.5),(-13,3.9,5.6),650,5),((-20,1,6.8),(-20,3.9,5.7),350,4),((-13,1,6.8),(-13,3.9,5.7),350,4)]):
    d=bpy.data.lights.new('PLW_Temporary_Review_Softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(f'PLW_Review_Light_{i}',d);review.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['temporary_review_light']=True
s.camera=bpy.data.objects['PLW_Facade_Beside_Control']
for o in review.objects:
    if o.type=='LIGHT':o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Windows.blend'),compress=True)
assert digest(SRC)==EXPECTED
print('PLW build saved',len(objects),'meshes',flush=True)
