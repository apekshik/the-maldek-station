"""R12-owned, repeatable texture and named material construction. No shared asset writes."""
import unreal,json,hashlib,re
from pathlib import Path
base=Path(__file__).resolve().parents[1]
baked=json.loads((base/'baked_materials.json').read_text())
manifest=json.loads((base/JOB.get('manifest','probe_manifest.json')).read_text())
for name,info in manifest['materials'].items():
 assert name in baked['materials'] and baked['materials'][name]['slot']==info['slot'],name
for key,row in baked['sets'].items():
 for channel,file in row['textures'].items():
  p=base/file;assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==row['files'][channel]['sha256'],str(p)
if JOB.get('dry_run'):
 RESULT={'valid_sets':len(baked['sets']),'valid_materials':len(manifest['materials']),'dry_run':True}
else:
 root='/Game/MaldekRefinement/R12';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
 textures={};masters={};instances={};report=[]
 def asset(name,folder,cls,factory):
  return lib.load_asset(folder+'/'+name) if lib.does_asset_exist(folder+'/'+name) else at.create_asset(name,folder,cls,factory)
 needed={baked['materials'][name]['set'] for name in manifest['materials']}
 for key,row in baked['sets'].items():
  if key not in needed:continue
  textures[key]={}
  for channel,file in row['textures'].items():
   path=root+'/Textures/'+Path(file).stem
   tex=lib.load_asset(path)
   if not tex:
    task=unreal.AssetImportTask();task.filename=str(base/file);task.destination_path=root+'/Textures';task.automated=True;task.save=True;task.replace_existing=True
    at.import_asset_tasks([task]);tex=lib.load_asset(path)
   assert tex,path
   compression=unreal.TextureCompressionSettings.TC_NORMALMAP if channel=='NormalDX' else unreal.TextureCompressionSettings.TC_MASKS if channel=='ORM' else unreal.TextureCompressionSettings.TC_DEFAULT
   if tex.get_editor_property('srgb')!=(channel=='BaseColor') or tex.get_editor_property('compression_settings')!=compression or (channel=='NormalDX' and tex.get_editor_property('flip_green_channel')):
    tex.set_editor_property('srgb',channel=='BaseColor');tex.set_editor_property('compression_settings',compression)
    if channel=='NormalDX':tex.set_editor_property('flip_green_channel',False)
    lib.save_loaded_asset(tex)
   textures[key][channel]=tex
 def family(info):
  n=info['source_material'].lower()
  if info['glass']:return 'Glass'
  for words,result in [(('emissive','lamp','lit_'),'Emissive'),(('concrete','ivory'),'Concrete'),(('gravel','parking'),'Gravel'),(('wood','timber','fabric','rubber','mattress'),'WoodFabricRubber'),(('galvanized','grating'),'Galvanized'),(('dark_steel','frame','oxidation'),'StructuralSteel')]:
   if any(w in n for w in words):return result
  return 'PaintedMetal'
 def master(kind,weather,key):
  ident=kind+('_Exterior' if weather else '_Interior')
  if ident in masters:return masters[ident]
  existing=lib.load_asset(root+'/Materials/Masters/M_R12_'+ident)
  if existing and not JOB.get('rebuild_masters'):
   masters[ident]=existing;return existing
  mat=asset('M_R12_'+ident,root+'/Materials/Masters',unreal.Material,unreal.MaterialFactoryNew())
  ml.delete_all_material_expressions(mat)
  mat.set_editor_property('two_sided',kind=='Glass')
  if kind=='Glass':mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
  def node(cls,x,y):return ml.create_material_expression(mat,cls,x,y)
  def connect(a,out,b,inp):assert ml.connect_material_expressions(a,out,b,inp),(out,inp)
  samples={}
  for i,ch in enumerate(['BaseColor','NormalDX','ORM']):
   n=node(unreal.MaterialExpressionTextureSampleParameter2D,-900,i*240);n.set_editor_property("parameter_name",ch);n.set_editor_property("texture",textures[key][ch])
   n.set_editor_property("sampler_type",unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if ch=='NormalDX' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if ch=='ORM' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
   samples[ch]=n
  if kind=='Glass':
   for ch,out,prop in [('BaseColor','RGB',unreal.MaterialProperty.MP_BASE_COLOR),('NormalDX','RGB',unreal.MaterialProperty.MP_NORMAL),('ORM','G',unreal.MaterialProperty.MP_ROUGHNESS)]:ml.connect_material_property(samples[ch],out,prop)
   opacity=node(unreal.MaterialExpressionScalarParameter,-400,700);opacity.set_editor_property("parameter_name","Opacity");opacity.set_editor_property("default_value",.18);ml.connect_material_property(opacity,'',unreal.MaterialProperty.MP_OPACITY)
  else:
   mat.set_editor_property('use_material_attributes',True)
   attrs=node(unreal.MaterialExpressionMakeMaterialAttributes,-300,0)
   for ch,out,inp in [('BaseColor','RGB','BaseColor'),('NormalDX','RGB','Normal'),('ORM','R','AmbientOcclusion'),('ORM','G','Roughness'),('ORM','B','Metallic')]:connect(samples[ch],out,attrs,inp)
   color=node(unreal.MaterialExpressionVectorParameter,-900,800);color.set_editor_property("parameter_name","EmissionColor");color.set_editor_property("default_value",unreal.LinearColor(0,0,0,1))
   power=node(unreal.MaterialExpressionScalarParameter,-900,1000);power.set_editor_property("parameter_name","EmissionStrength");power.set_editor_property("default_value",0)
   mul=node(unreal.MaterialExpressionMultiply,-500,800);connect(color,'RGB',mul,'A');connect(power,'',mul,'B');connect(mul,'',attrs,'EmissiveColor')
   output=attrs
   if weather:
    fn=lib.load_asset('/Game/UltraDynamicSky/Materials/Weather/Surface_Weather_Effects');assert fn
    wf=node(unreal.MaterialExpressionMaterialFunctionCall,0,0);wf.set_material_function(fn)
    enabled=node(unreal.MaterialExpressionStaticBool,-250,650);enabled.set_editor_property("value",True)
    connect(enabled,'',wf,'Apply Wetness');connect(enabled,'',wf,'Apply Snow / Dust');connect(attrs,'',wf,'Material Attributes');output=wf
   ml.connect_material_property(output,'',unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
  mat.set_editor_property('usage_flag_warnings',False) if False else None
  ml.recompile_material(mat);lib.save_loaded_asset(mat);masters[ident]=mat;return mat
 for name,info in manifest['materials'].items():
  entry=baked['materials'][name];key=entry['set'];kind=family(info)
  indoor=info.get('exposure')=='Indoor' or any(s in name.lower() for s in ['interior','enamel','fabric','mattress'])
  weather=not indoor and kind not in ['Glass','Emissive'] and not JOB.get('inspection_dry')
  parent=master(kind,weather,key)
  mi=asset(('MI_Dry_' if JOB.get('inspection_dry') else 'MI_')+info['slot'],root+'/Materials/Instances',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
  pm=lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+info['physical_surface']);assert pm
  explicit={str(v.parameter_info.name):v.parameter_value for v in mi.get_editor_property('texture_parameter_values')}
  unchanged=mi.get_editor_property('parent')==parent and mi.get_editor_property('phys_material')==pm and all(explicit.get(ch)==tex for ch,tex in textures[key].items())
  if unchanged and kind!='Glass':
   ec=info.get('emission_color',[0,0,0,1]);actual=ml.get_material_instance_vector_parameter_value(mi,'EmissionColor')
   unchanged=abs(ml.get_material_instance_scalar_parameter_value(mi,'EmissionStrength')-info.get('emission_strength',0))<.00001 and max(abs(x-y) for x,y in zip([actual.r,actual.g,actual.b,actual.a],ec))<.00001
  if unchanged:
   instances[info['slot']]=mi;report.append({'slot':info['slot'],'instance':mi.get_path_name(),'master':parent.get_path_name(),'texture_set':key,'weather':weather,'physical_material':pm.get_path_name(),'reused':True});continue
  ml.set_material_instance_parent(mi,parent)
  # Explicit overrides remain stable if the master's preview/default texture changes on rerun.
  mi.set_editor_property('texture_parameter_values',[unreal.TextureParameterValue(parameter_info=unreal.MaterialParameterInfo(name=ch),parameter_value=tex) for ch,tex in textures[key].items()])
  ml.update_material_instance(mi)
  for ch,tex in textures[key].items():
   ml.set_material_instance_texture_parameter_value(mi,ch,tex)
   actual=ml.get_material_instance_texture_parameter_value(mi,ch)
   assert actual and actual.get_path_name()==tex.get_path_name(),(name,ch,str(actual))
  if kind!='Glass':
   ec=info.get('emission_color',[0,0,0,1]);ml.set_material_instance_vector_parameter_value(mi,'EmissionColor',unreal.LinearColor(*ec))
   ml.set_material_instance_scalar_parameter_value(mi,'EmissionStrength',info.get('emission_strength',0))
  pm=lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+info['physical_surface']);assert pm
  mi.set_editor_property('phys_material',pm);ml.update_material_instance(mi);lib.save_loaded_asset(mi);instances[info['slot']]=mi
  report.append({'slot':info['slot'],'instance':mi.get_path_name(),'master':parent.get_path_name(),'texture_set':key,'weather':weather,'physical_material':pm.get_path_name()})
 for row in manifest['chunks']:
  if JOB.get('inspection_dry'):continue
  path=JOB.get('mesh_path',root+'/Probe/Meshes')+'/'+row['name'];mesh=lib.load_asset(path)
  if not mesh:continue
  for i,s in enumerate(mesh.static_materials):
   slot=str(s.material_slot_name);assert slot in instances,(path,slot);mesh.set_material(i,instances[slot])
  lib.save_loaded_asset(mesh)
 RESULT={'success':True,'materials':report,'texture_sets':len(textures),'normal_green_flipped_on_import':False}
 (base/JOB.get('report','probe_materials.json')).write_text(json.dumps(RESULT,indent=2))
