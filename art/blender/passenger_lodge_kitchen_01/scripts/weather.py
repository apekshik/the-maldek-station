"""Non-destructive CC0 texture finish study; run with Blender --background --python."""
import bpy, json, hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
W=OUT/'weathering'; W.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen.blend'))
s=bpy.data.scenes['PLK_Fitted_Review']; bpy.context.window.scene=s; s.frame_set(1)
assets=bpy.data.collections['PLK_Assets']
def geometry():
 result={}
 for o in s.objects:
  data={'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None}
  if o.type=='MESH':data['mesh']=hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
  result[o.name]=data
 return result
before=geometry()
refs={o.name:[m.name if m else None for m in o.data.materials] for o in s.objects if o not in list(assets.all_objects) and o.type in {'MESH','FONT'}}
used={m for o in assets.all_objects if o.type in {'MESH','FONT'} for m in o.data.materials if m}
mapping={}; manifest=[]
for original in sorted(used,key=lambda m:m.name):
 if original.name in {'PLK_Chalk_lettering','PLK_Red_index'}:continue
 m=original.copy();m.name='PLK_Worn_'+original.name.removeprefix('PLK_').removeprefix('PL03_').removeprefix('VF06_');mapping[original]=m
 m['finish_study']='Sheltered abandoned interior; CC0 maps, procedural directional dust and cavity dirt; Blender-only until baked.'
 nt=m.node_tree; nodes=nt.nodes; links=nt.links
 p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 def node(t,label):
  n=nodes.new(t);n.label=label;n.name=label;return n
 def wire(val,sock):
  if isinstance(val,(int,float)):sock.default_value=val
  else:links.new(val,sock)
 def math(op,a,b=0):
  n=node('ShaderNodeMath',op);n.operation=op;wire(a,n.inputs[0]);wire(b,n.inputs[1]);return n.outputs[0]
 def mix(a,b,f,label):
  n=node('ShaderNodeMixRGB',label);wire(f,n.inputs[0])
  for v,inp in [(a,n.inputs[1]),(b,n.inputs[2])]:
   if isinstance(v,tuple):inp.default_value=v
   else:links.new(v,inp)
  return n.outputs[0]
 tc=node('ShaderNodeTexCoord','Component coordinates in metres')
 def tex(file,scale=1,color=False,projection='BOX'):
  n=node('ShaderNodeTexImage',file);n.image=bpy.data.images.load(str(W/'textures'/file),check_existing=True);n.image.colorspace_settings.name='sRGB' if color else 'Non-Color';n.projection=projection;n.projection_blend=.25
  v=node('ShaderNodeVectorMath','Physical texture frequency');v.operation='SCALE';links.new(tc.outputs['Object'],v.inputs[0]);v.inputs[3].default_value=scale;links.new(v.outputs[0],n.inputs['Vector'])
  return n.outputs['Color']
 base=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else tuple(p.inputs['Base Color'].default_value)
 metal='stainless' in m.name or 'Chrome' in m.name
 glass='glass' in m.name
 wood='Pine' in m.name or 'birch' in m.name
 laminate='laminate' in m.name
 porcelain='Porcelain' in m.name
 rubber='rubber' in m.name
 if wood:
  # Box-projected colour/roughness only. Tangent normal is retained as a source
  # asset but deliberately unused without a dedicated aligned UV unwrap.
  worn=tex('wood_cabinet_worn_long_diff_2k.jpg',1.0,True)
  base=mix((.34,.245,.145,1),worn,.78,'Tinted worn furniture grain')
 dust=tex('SurfaceImperfections015_2K-JPG_Opacity.jpg',1/.65)
 geo=node('ShaderNodeNewGeometry','Surface direction')
 sep=node('ShaderNodeSeparateXYZ','Upward facing');links.new(geo.outputs['Normal'],sep.inputs[0])
 up=math('MAXIMUM',sep.outputs['Z'],0)
 up=math('POWER',up,3)
 deposit=math('MULTIPLY',dust,math('ADD',math('MULTIPLY',up,.56),.045))
 ao=node('ShaderNodeAmbientOcclusion','Short range seam dirt');ao.inputs['Distance'].default_value=.045;ao.samples=8
 cavity=math('MULTIPLY',math('SUBTRACT',1,ao.outputs['AO']),.38 if not glass else .1)
 base=mix(base,(.095,.072,.043,1),cavity,'Dark residue in joints')
 base=mix(base,(.39,.335,.255,1),deposit,'Settled warm grey dust')
 roughbase=.28 if metal else .08 if glass else .48 if rubber else .64
 rough=math('ADD',roughbase,math('MULTIPLY',deposit,.55))
 bump_height=dust
 if metal or laminate or glass or rubber or 'enamel' in m.name or 'paint' in m.name:
  scratches=tex('Scratches004_2K-JPG_Opacity.jpg',3)
  smear=tex('Smear004_2K-JPG_Roughness.jpg',4)
  rough=math('ADD',rough,math('MULTIPLY',smear,.20 if metal else .12 if glass else .1))
  rough=math('ADD',rough,math('MULTIPLY',scratches,.16))
  bump_height=math('ADD',math('MULTIPLY',dust,.3),math('MULTIPLY',scratches,.3))
 if metal or porcelain:
  water=tex('SurfaceImperfections001_2K-JPG_Opacity.jpg',5)
  mineral=math('MULTIPLY',water,.14 if metal else .11)
  base=mix(base,(.53,.48,.36,1),mineral,'Thin dried mineral spotting')
  rough=math('ADD',rough,math('MULTIPLY',water,.18))
 if laminate:
  # Sparse rings at plausible cup scale (atlas spans ~2.5m). Up faces only.
  rings=tex('SurfaceImperfections007_2K-JPG_Opacity.jpg',.4,projection='FLAT')
  factor=math('MULTIPLY',math('POWER',rings,1.6),math('MULTIPLY',up,.42))
  base=mix(base,(.115,.065,.023,1),factor,'Faint old cup rings on laminate tops')
 if wood:
  wr=tex('wood_cabinet_worn_long_rough_2k.jpg',1)
  rough=math('ADD',.43,math('MULTIPLY',wr,.42))
 rough=math('MINIMUM',rough,.94)
 links.new(base,p.inputs['Base Color']);links.new(rough,p.inputs['Roughness'])
 if metal:links.new(math('SUBTRACT',.88,math('MULTIPLY',deposit,.65)),p.inputs['Metallic'])
 bump=node('ShaderNodeBump','Microscopic film and hairline scuffs');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00016;links.new(bump_height,bump.inputs['Height'])
 if p.inputs['Normal'].is_linked:links.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
 links.new(bump.outputs['Normal'],p.inputs['Normal'])
 for i,n in enumerate(nodes):n.location=((i%7)*240,-(i//7)*230)
 manifest.append({'clean_material':original.name,'weathered_material':m.name,'blender_only':True,'textures':sorted({n.image.name for n in nodes if n.type=='TEX_IMAGE'}),'treatment':{'directional_dust':True,'cavity_dirt':True,'water_residue':metal or porcelain,'fine_scuffs':metal or laminate or glass or rubber or 'enamel' in m.name or 'paint' in m.name,'cup_rings':laminate,'worn_wood':wood}})
for o in assets.all_objects:
 if o.type in {'MESH','FONT'}:
  for slot in o.material_slots:
   if slot.material in mapping:slot.material=mapping[slot.material]
assert geometry()==before,'Geometry or transform changed'
assert refs=={o.name:[m.name if m else None for m in o.data.materials] for o in s.objects if o.name in refs},'Reference material changed'
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath and Path(bpy.path.abspath(image.filepath)).exists():
  image.pack()
  if Path(bpy.path.abspath(image.filepath)).parent==W/'textures':image.filepath='//textures/'+Path(image.filepath).name
(W/'material_manifest.json').write_text(json.dumps(manifest,indent=2))
(W/'geometry_baseline.json').write_text(json.dumps({'clean_scene_object_count':len(before),'geometry_and_transform_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()},indent=2))
assets['finish_variant']='PLK weathered / sheltered abandonment; append this OR clean assets, never both.'
s.camera=bpy.data.objects['PLK_REVIEW_03_Staff_entry']
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Maldek_Passenger_Lodge_Kitchen_Weathered.blend'),relative_remap=False)
bpy.data.libraries.write(str(W/'PLK_Assets_Weathered.blend'),{assets},fake_user=True)
# Reopen saved deliverable, compare exact mesh vertices, polygon indices, parents
# and transforms of ALL scene objects, including reference context.
bpy.ops.wm.open_mainfile(filepath=str(W/'Maldek_Passenger_Lodge_Kitchen_Weathered.blend'))
s=bpy.data.scenes['PLK_Fitted_Review'];bpy.context.window.scene=s;s.frame_set(1)
assert geometry()==before
images=[i for i in bpy.data.images if i.source=='FILE' and i.name in {t for r in manifest for t in r['textures']}]
assert all(i.packed_file for i in images)
(W/'verification.json').write_text(json.dumps({'saved_reopened':True,'all_scene_geometry_transforms_parents_unchanged':True,'reference_material_slots_unchanged':True,'new_material_count':len(manifest),'used_texture_count':len(images),'all_used_textures_packed':True,'geometry_clearances':'Inherited unchanged from clean verification.json and mechanism_contacts.json; no engine collision tested.','clean_blend_sha256':hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Kitchen.blend').read_bytes()).hexdigest()},indent=2))
print('WEATHERED PACKAGE VERIFIED',flush=True)
