import unreal
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
for name in ['M_R05_Local_Terrain','M_R03_Wet_Gravel']:
 m=lib.load_asset('/Game/MaldekRefinement/R05/Materials/'+name);visited=set()
 def visit(n):
  if not n or n.get_path_name() in visited:return
  visited.add(n.get_path_name())
  if isinstance(n,unreal.MaterialExpressionTextureSample):
   normal=n.sampler_type==unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
   n.texture=lib.load_asset('/Game/MWLandscapeAutoMaterial/Textures/Ground/TEX_MWAM_Stones_'+('nrm' if normal else 'col'))
  for child in ml.get_inputs_for_material_expression(m,n):visit(child)
 for prop in [unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES]:visit(ml.get_material_property_input_node(m,prop))
 ml.recompile_material(m);lib.save_loaded_asset(m)
