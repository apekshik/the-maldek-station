import unreal
ROOT='/Game/MaldekRefinement'
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
mesh=lib.load_asset(ROOT+'/Meshes/SM_R04_Local_Terrain')
path=ROOT+'/Materials/M_R04_Local_Terrain'
mat=lib.load_asset(path) if lib.does_asset_exist(path) else at.create_asset('M_R04_Local_Terrain',ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
ml.delete_all_material_expressions(mat);mat.set_editor_property('use_material_attributes',True)
attributes=ml.create_material_expression(mat,unreal.MaterialExpressionMakeMaterialAttributes,0,0)
base='/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_03_ydzkbhu/High/SM_ydzkbhu_tier_1/Textures/'
diff=ml.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,-100);diff.texture=lib.load_asset(base+'T_ydzkbhu_4k_B')
assert ml.connect_material_expressions(diff,'RGB',attributes,'BaseColor')
normal=ml.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,100);normal.texture=lib.load_asset(base+'T_ydzkbhu_4k_N');normal.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
assert ml.connect_material_expressions(normal,'RGB',attributes,'Normal')
rough=ml.create_material_expression(mat,unreal.MaterialExpressionConstant,-500,350);rough.r=.88
assert ml.connect_material_expressions(rough,'',attributes,'Roughness')
weather=ml.create_material_expression(mat,unreal.MaterialExpressionMaterialFunctionCall,300,0)
weather.set_material_function(lib.load_asset('/Game/UltraDynamicSky/Materials/Weather/Surface_Weather_Effects'))
enabled=ml.create_material_expression(mat,unreal.MaterialExpressionStaticBool,0,500);enabled.set_editor_property('value',True)
assert ml.connect_material_expressions(enabled,'',weather,'Apply Wetness')
assert ml.connect_material_expressions(enabled,'',weather,'Apply Snow / Dust')
for pin,value in [('Wet Roughness',.65),('Snow / Dust Roughness',.85)]:
 parameter=ml.create_material_expression(mat,unreal.MaterialExpressionConstant,100,650);parameter.r=value
 assert ml.connect_material_expressions(parameter,'',weather,pin)
assert ml.connect_material_expressions(attributes,'',weather,'Material Attributes')
assert ml.connect_material_property(weather,'',unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
ml.recompile_material(mat);lib.save_loaded_asset(mat)
mesh.set_material(0,mat);lib.save_loaded_asset(mesh)

