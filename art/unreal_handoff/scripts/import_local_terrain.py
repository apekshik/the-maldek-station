import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ROOT='/Game/MaldekRefinement'
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
task=unreal.AssetImportTask();task.filename=str(OUT/'fbx/SM_R04_Local_Terrain.fbx');task.destination_path=ROOT+'/Meshes';task.destination_name='SM_R04_Local_Terrain';task.automated=True;task.save=True;task.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_textures=False;opt.import_materials=False;opt.import_as_skeletal=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
data=opt.static_mesh_import_data;data.combine_meshes=True;data.auto_generate_collision=False;data.convert_scene=True;data.convert_scene_unit=True;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
task.options=opt;at.import_asset_tasks([task])
mesh=lib.load_asset(ROOT+'/Meshes/SM_R04_Local_Terrain')
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
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
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='R04_Local_Terrain'),None)
origin=json.loads((OUT/'working_level_report.json').read_text())['station_origin']
if not actor:actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*origin),unreal.Rotator(pitch=0,yaw=180,roll=0))
actor.set_actor_label('R04_Local_Terrain');actor.set_folder_path('R04_Terrain')
actor.static_mesh_component.set_static_mesh(mesh);actor.static_mesh_component.set_collision_profile_name('BlockAll')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('R04_LOCAL_TERRAIN_COMPLETE')
