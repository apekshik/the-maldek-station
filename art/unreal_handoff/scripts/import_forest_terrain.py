import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';root='/Game/MaldekRefinement/ForestTest';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ml=unreal.MaterialEditingLibrary
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Forest_Approach_Test'
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/'SM_ForestTerrain.fbx');t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;t.options=opt;at.import_asset_tasks([t])
mesh=lib.load_asset(root+'/Meshes/SM_ForestTerrain');mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
m=lib.load_asset(root+'/Materials/M_Forest_Soil') or at.create_asset('M_Forest_Soil',root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
noise=ml.create_material_expression(m,unreal.MaterialExpressionNoise);noise.set_editor_property('scale',.08);noise.set_editor_property('levels',3)
a=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);a.constant=unreal.LinearColor(.055,.037,.022,1)
b=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);b.constant=unreal.LinearColor(.14,.10,.065,1)
lerp=ml.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate)
ml.connect_material_expressions(a,'',lerp,'A');ml.connect_material_expressions(b,'',lerp,'B');ml.connect_material_expressions(noise,'',lerp,'Alpha');ml.connect_material_property(lerp,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=ml.create_material_expression(m,unreal.MaterialExpressionConstant);r.r=.94;ml.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS);ml.recompile_material(m);lib.save_loaded_asset(m)
mesh.set_material(0,m);lib.save_loaded_asset(mesh)
a=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='R04_Local_Terrain');a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,m)
# The original landscape remains below the added shoulders; local mesh collision supplies the new ground.
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
