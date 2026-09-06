import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ROOT='/Game/MaldekRefinement/R05';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='BlockOut_R05'
at=unreal.AssetToolsHelpers.get_asset_tools();task=unreal.AssetImportTask();task.filename=str(OUT/'revision05/fbx/SM_R05_Local_Terrain.fbx');task.destination_path=ROOT+'/Meshes';task.automated=True;task.save=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True
task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(ROOT+'/Meshes/SM_R05_Local_Terrain');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
mat=lib.duplicate_asset('/Game/MaldekRefinement/Materials/M_R04_Local_Terrain',ROOT+'/Materials/M_R05_Local_Terrain');assert mat
weather=ml.get_material_property_input_node(mat,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
pins=ml.get_material_expression_input_names(weather)
(OUT/'revision05/weather_pins.json').write_text(json.dumps([str(p) for p in pins]))
snow=ml.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);snow.set_editor_property('constant',unreal.LinearColor(.30,.35,.43,1))
for pin in pins:
 if 'color' in str(pin).lower() and ('snow' in str(pin).lower()):assert ml.connect_material_expressions(snow,'',weather,str(pin))
ml.recompile_material(mat);lib.save_loaded_asset(mat);mesh.set_material(0,mat);lib.save_loaded_asset(mesh)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
a=next(a for a in actors if a.get_actor_label()=='R04_Local_Terrain');a.static_mesh_component.set_static_mesh(mesh)
a.static_mesh_component.set_collision_profile_name('BlockAll')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT/'revision05/terrain_import.json').write_text(json.dumps({'saved':True,'mesh':mesh.get_path_name(),'snow_pins':[str(p) for p in pins if 'snow' in str(p).lower()]}))
