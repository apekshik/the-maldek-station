import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parents[1];ART=OUT.parent;SOURCE=ART/'west_services_01/Maldek_West_Services_Blockout.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==json.loads((SOURCE.parent/'delivery.json').read_text())['sha256']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['West_Services_Combined'];bpy.context.window.scene=s;s.name='Station_West_Services_Integrated';s.frame_set(1);bpy.context.view_layer.update()
context={o.name:[list(r) for r in o.matrix_world] for o in s.objects};retired=[];packages=[]
roots=bpy.data.collections.new('WS02_ASSEMBLY_ROOTS');s.collection.children.link(roots)
for folder,blend,col,mkey,dkey,origin in [
 ('west_services_parcels_01','Maldek_Parcels_Office.blend','WSP_ASSETS','local_to_world','delete_exact',(-37.45,-5,4.6)),
 ('west_services_rescue_01','Maldek_Rescue_Hut_Editable.blend','WSR_ASSETS','local_to_station_matrix','delete_exactly',(-37.45,0,4.6)),
 ('west_services_power_01','Maldek_Emergency_Power.blend','WSE_ASSETS','matrix_local_to_world','remove_objects',(-37.45,-5,1.2))]:
 p=ART/folder;a=json.loads((p/'assembly.json').read_text());d=json.loads((p/'delivery.json').read_text());assert json.loads((p/'verification.json').read_text())['passed']
 h=sha(p/blend)
 expected=d.get('asset_sha256') or d.get('files',{}).get(blend,{}).get('sha256') or d.get('sha256',{}).get(blend) or d.get('hashes',{}).get(blend)
 # Recorded file digests are retained in reconciliation even where schema varies.
 if expected:assert h==expected,(folder,h,expected)
 for n in a[dkey]:assert n in s.objects;nob=bpy.data.objects[n];retired.append(n);bpy.data.objects.remove(nob,do_unlink=True)
 with bpy.data.libraries.load(str(p/blend),link=False) as (src,dst):dst.collections=[col]
 c=dst.collections[0];s.collection.children.link(c)
 root=bpy.data.objects.new('WS02_'+col+'_Assembly',None);roots.objects.link(root);root.matrix_world=Matrix(a[mkey])
 for ob in c.all_objects:
  if ob.parent is None:ob.parent=root
 s.frame_set(1);bpy.context.view_layer.update()
 packages.append({'package':folder,'file':blend,'sha256':h,'collection':col,'matrix':a[mkey],'objects':{ob.name:{'parent':ob.parent.name if ob.parent else None,'world_matrix':[list(r) for r in ob.matrix_world],'type':ob.type,'material_slots':[m.name if m else None for m in ob.data.materials] if hasattr(ob.data,'materials') else []} for ob in c.all_objects},'deleted_proxies':a[dkey]})
print('APPENDED',[(p['collection'],len(p['objects'])) for p in packages],flush=True)
# A derived-file path is required by the supplied shell patch guard.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Station_West_Integrated.blend'))
# Execute with a single shared namespace so the supplied function has bpy/FROZEN globals.
ns={'__name__':'integration_import','__file__':str(ART/'west_services_power_01/scripts/patch_world.py')};exec(compile((ART/'west_services_power_01/scripts/patch_world.py').read_text(),'patch_world','exec'),ns);ns['apply_world_patch']()
cols={}
for n in ['WS02_WRAP_PLATFORM','WS02_STORAGE_CLUTTER','WS02_SHARED_FINISH','WS02_REVIEW_ONLY']:
 c=bpy.data.collections.new(n);s.collection.children.link(c);cols[n]=c
cur=cols['WS02_WRAP_PLATFORM']
def material(n,color,rough=.7,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
con=material('WS02_Aged_Concrete',(.32,.34,.32));steel=material('WS02_Galvanized',(.34,.4,.41),.42,.65);green=material('WS02_Petrol_Paint',(.055,.16,.145),.55,.2);wood=material('WS02_Pine_Cladding',(.29,.2,.12));cream=material('WS02_Warm_Plaster',(.67,.62,.5));dark=material('WS02_Rubber',(.025,.032,.03));rust=material('WS02_Dull_Rust',(.24,.115,.065),.85,.2)
# Original procedural wear; local object-generated noise, no downloaded textures.
for m,scale,strength in [(con,14,.08),(wood,7,.09)]:
 nt=m.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.05;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
def box(n,lo,hi,m=con,bevel=0):
 vs=[(x,y,z) for z in [lo[2],hi[2]] for y in [lo[1],hi[1]] for x in [lo[0],hi[0]]];fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
 me=bpy.data.meshes.new('WS02_'+n);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('WS02_'+n,me);cur.objects.link(ob);me.materials.append(m)
 if bevel:mod=ob.modifiers.new('Edge light','BEVEL');mod.width=bevel;mod.segments=2
 return ob
def tube(n,a,b,r=.035,m=green):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,0,1)))
 if u.length<.01:u=v.cross(Vector((0,1,0)))
 u.normalize();w=v.cross(u);vs=[p+r*(math.cos(i*math.tau/12)*u+math.sin(i*math.tau/12)*w) for p in [a,b] for i in range(12)];fs=[tuple(reversed(range(12))),tuple(range(12,24))]+[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)]
 me=bpy.data.meshes.new('WS02_'+n);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('WS02_'+n,me);cur.objects.link(ob);me.materials.append(m);return ob
def rail(n,a,b):
 for h in [.55,1.1]:tube(n+'_bar',Vector(a)+Vector((0,0,h)),Vector(b)+Vector((0,0,h)))
 N=max(1,math.ceil((Vector(b)-Vector(a)).length/1.5))
 for i in range(N+1):
  p=Vector(a).lerp(Vector(b),i/N);tube(n+'_post',p,p+Vector((0,0,1.1)),.042);box(n+'_foot',(p.x-.075,p.y-.075,p.z),(p.x+.075,p.y+.075,p.z+.018),steel)
# Replace only the prior narrow lower deck and its obsolete perimeter guard.
for ob in list(s.objects):
 if ob.name in ['WS_LowerLanding','WS_LowerWalk'] or ob.name.startswith(('WS_LowerEnd','WS_LowerOuter','WS_LowerSouth')):
  retired.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
# Four nonoverlapping slabs form a continuous ring; existing base slab owns the centre.
rects=[(-40.45,-37.45,-7.5,10.6),(-37.45,-31.45,-7.5,-5),(-31.45,-28.95,-7.5,10.6),(-37.45,-31.45,5,10.6)]
for i,(x0,x1,y0,y1) in enumerate(rects):box('WrapDeck_'+str(i),(x0,y0,1),(x1,y1,1.2))
rail('WestOuter',(-40.45,-7.5,1.2),(-40.45,10.6,1.2));rail('NorthOuter',(-40.45,10.6,1.2),(-28.95,10.6,1.2));rail('EastOuter',(-28.95,10.6,1.2),(-28.95,-7.5,1.2));rail('SouthOuter',(-28.95,-7.5,1.2),(-40.45,-7.5,1.2))
# Block off the low-headroom void under the flight; route around its north side.
rail('UnderStairSouth',(-37.05,6.0,1.2),(-34.95,6.0,1.2));rail('UnderStairNorth',(-37.05,8.4,1.2),(-34.95,8.4,1.2))
# Support new deck against inherited Blender terrain, without changing it.
terrain=bpy.data.objects['R11_Current_Terrain'];inv=terrain.matrix_world.inverted();support=[]
for x in [-40.15,-29.25]:
 for y in [-7.2,-2,3.5,10.25]:
  ok,pt,nn,idx=terrain.ray_cast(inv@Vector((x,y,100)),Vector((0,0,-1)),distance=500);assert ok;ground=(terrain.matrix_world@pt).z
  box('DeckPier',(x-.12,y-.12,ground-.35),(x+.12,y+.12,1),con);support.append({'xy':[x,y],'ground':ground,'toe':ground-.35})
for y in [-7.2,10.25]:
 box('RingBeam',(-40.3,y-.10,.73),(-29.1,y+.1,1),steel)
for x in [-40.15,-29.25]:box('LongBeam',(x-.1,-7.3,.73),(x+.1,10.4,1),steel)
# Lightly detailed common architecture; change finishes only on the existing shared meshes.
cur=cols['WS02_SHARED_FINISH']
for ob in bpy.data.collections['WS_SHARED_STRUCTURE'].objects:
 if ob.type!='MESH':continue
 if ob.name.startswith(('WS_Base','WS_UpperSlab','WS_Porch','WS_Ramp','WS_UpperStep','WS_ServiceStep')):
  ob.data.materials.clear();ob.data.materials.append(con)
 if ob.name.startswith(('WS_UpperEast','WS_UpperWest','WS_UpperNorth','WS_UpperSouth','WS_SharedPartyWall')):
  ob.data.materials.clear();ob.data.materials.append(wood);ob.data.materials.append(cream)
  for f in ob.data.polygons:
   inside=('UpperEast' in ob.name and f.normal.x<-.5) or ('UpperWest' in ob.name and f.normal.x>.5) or ('UpperNorth' in ob.name and f.normal.y<-.5) or ('UpperSouth' in ob.name and f.normal.y>.5) or ('SharedParty' in ob.name)
   f.material_index=1 if inside else 0
# Timber battens on the unperforated west wall; discreet joints, kept off all apertures.
for i in range(39):
 y=-4.86+i*.25;box('WestBatten',(-37.475,y,4.62),(-37.448,y+.032,7.29),wood,.003)
for y in [-5.018,5]:
 for i in range(23):
  x=-37.20+i*.24;box('EndBatten',(x,y,4.62),(x+.032,y+.018,7.29),wood,.003)
for z in [4.61,7.2]:
 box('WestTimberBand',(-37.49,-5.03,z),(-37.455,5.03,z+.08),wood,.004)
# Roof seams and gutters follow the actual roof pitch; no extra flat roof shell.
cur=bpy.data.collections['WS_SHARED_ROOF']
def roofz(x):return 7.38+(x+37.85)*(.77/3.4) if x<=-34.45 else 8.15-(x+34.45)*(.77/5.3)
for i in range(19):
 y=-5.37+i*.59
 for xa,xb in [(-37.85,-34.45),(-34.45,-29.15)]:tube('RoofSeam',(xa,y,roofz(xa)+.17),(xb,y,roofz(xb)+.17),.018,green)
tube('RidgeCap',(-34.45,-5.48,8.32),(-34.45,5.48,8.32),.055,green)
for x in [-37.86,-29.14]:
 tube('Gutter',(x,-5.5,7.42),(x,5.5,7.42),.075,steel)
 tube('Downpipe',(x,5.52,7.42),(x,5.52,1.45),.045,steel)
 tube('DrainShoe',(x,5.52,1.45),(x,5.9,1.27),.045,steel)
# Loose utility clutter on the spare south/east platform; independent props, no objectives.
cur=cols['WS02_STORAGE_CLUTTER']
# Low stack of pallets and rough empty crates beside south wall; central route stays clear.
for tier in range(2):
 z=1.2+tier*.18
 for x in [-36.6,-35.7]:box('PalletRunner',(x,-6.10,z),(x+.10,-5.20,z+.10),wood,.006)
 for j in range(6):box('PalletSlat',(-36.65,-6.1+j*.16,z+.10),(-35.48,-5.98+j*.16,z+.14),wood,.005)
for x,y,z in [(-36.55,-5.97,1.56),(-35.92,-5.93,1.56),(-36.4,-5.95,2.13)]:
 for k in range(3):
  zz=z+k*.16
  box('CrateSlat',(x,y,zz),(x+.54,y+.04,zz+.12),wood,.005);box('CrateSlat',(x,y+.46,zz),(x+.54,y+.50,zz+.12),wood,.005)
  box('CrateEnd',(x,y+.04,zz),(x+.04,y+.46,zz+.12),wood,.005);box('CrateEnd',(x+.5,y+.04,zz),(x+.54,y+.46,zz+.12),wood,.005)
 box('CrateBase',(x,y,z-.04),(x+.54,y+.5,z),wood)
for i in range(5):
 tube('PipeOffcut',(-31.2,1.1+i*.17,1.33),(-30.75,1.1+i*.17,2.4+i*.05),.06,rust)
# Spare boards laid in a short untidy stack, close to east wall.
for i in range(5):box('SpareBoard',(-31.32,3.2+i*.04,1.22+i*.045),(-30.75,4.7+i*.035,1.26+i*.045),wood,.004)
# A plain covered bundle sits beyond the north face, away from the stair and ring route.
box('StorageBundle',(-32.7,5.25,1.21),(-31.7,5.95,1.8),dark,.05)
# Record unchanged source context and exact package placement before final save.
s.frame_set(1);bpy.context.view_layer.update()
manifest={'source':str(SOURCE),'source_sha256':sha(SOURCE),'scene':s.name,'packages':packages,'retired_objects':retired,'shell_patch':json.loads((ART/'west_services_power_01/shell_patch.json').read_text()),'preserved_context_transforms':{n:v for n,v in context.items() if n not in retired},'platform':{'z':1.2,'outer_bounds':[-40.45,-28.95,-7.5,10.6],'rectangles':rects,'support_samples':support,'terrain_basis':'Inherited R11 Blender terrain only'},'new_collections':{n:[o.name for o in c.all_objects] for n,c in cols.items()},'source_limitations':'Blender assembly only; Unreal export/collision/lighting and live terrain fit remain pending'}
(OUT/'reconciliation.json').write_text(json.dumps(manifest,indent=2))
cur=cols['WS02_REVIEW_ONLY']
views=[('01_Station',(-61,36,30),(-21,-1,3),49),('02_Wrap_platform',(-52,24,18),(-34,1,3.5),25),('03_Upper_cutaway',(-44,-14,23),(-34,0,5),21),('04_Lower_wrap_plan',(-34,1,32),(-34,1,1.2),24),('05_Arrival',(-25,-18,10),(-34,0,4.5),27)]
for name,pos,target,scale in views:
 d=bpy.data.cameras.new('WS02_'+name);o=bpy.data.objects.new(d.name,d);cur.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
s.camera=bpy.data.objects['WS02_01_Station'];s.frame_start=1;s.frame_end=80
for f,n in [(1,'NORMAL / CLOSED'),(40,'ROOMS OPEN / RESCUE READY'),(80,'RESCUE EQUIPMENT OPEN')]:s.timeline_markers.new(n,frame=f)
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_cavity=True;s.display.shading.show_shadows=True
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Station_West_Integrated.blend'))
print('INTEGRATED COMPLETE',flush=True)
