import unreal
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;root='/Game/MaldekRefinement/R05/Materials/'
mi=lib.load_asset(root+'MI_Landscape_CohesiveSnow')
ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowWorldPosition',35000)
lib.save_loaded_asset(mi)
mat=lib.load_asset(root+'M_R05_Local_Terrain');weather=ml.get_material_property_input_node(mat,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
mask=ml.create_material_expression(mat,unreal.MaterialExpressionConstant);mask.r=.15
assert ml.connect_material_expressions(mask,'',weather,'Mask Snow / Dust Coverage')
ml.recompile_material(mat);lib.save_loaded_asset(mat)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
