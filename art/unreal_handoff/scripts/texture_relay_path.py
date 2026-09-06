import unreal
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
m=lib.load_asset('/Game/MaldekRefinement/R05/Materials/M_R03_Wet_Gravel')
ml.delete_all_material_expressions(m)
pos=ml.create_material_expression(m,unreal.MaterialExpressionWorldPosition)
mask=ml.create_material_expression(m,unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',True);assert ml.connect_material_expressions(pos,'',mask,'')
scale=ml.create_material_expression(m,unreal.MaterialExpressionDivide);scale.set_editor_property('const_b',250);ml.connect_material_expressions(mask,'',scale,'A')
t=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);t.texture=lib.load_asset('/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_03_ydzkbhu/High/SM_ydzkbhu_tier_1/Textures/T_ydzkbhu_4k_B');assert t.texture
ml.connect_material_expressions(scale,'',t,'UVs')
mult=ml.create_material_expression(m,unreal.MaterialExpressionMultiply);mult.set_editor_property('const_b',.5);ml.connect_material_expressions(t,'RGB',mult,'A');ml.connect_material_property(mult,'',unreal.MaterialProperty.MP_BASE_COLOR)
ml.recompile_material(m);lib.save_loaded_asset(m)
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='R04_08_Fuel_Yard')
a.static_mesh_component.set_static_mesh(lib.load_asset('/Game/MaldekRefinement/Meshes/SM_R04_08_Fuel_Yard'))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()


