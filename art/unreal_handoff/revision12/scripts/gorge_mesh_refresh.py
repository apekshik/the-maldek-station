"""Reimport the perimeter correction and assert the finished ground material slot."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/'SM_Station_Gorge_Terrain.fbx');t.destination_path='/Game/MaldekRefinement/R12/Gorge/Meshes';t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;t.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset('/Game/MaldekRefinement/R12/Gorge/Meshes/SM_Station_Gorge_Terrain');material=unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Woodland_Ground');assert material
assert len(mesh.get_editor_property('static_materials'))>=1
for i in range(len(mesh.get_editor_property('static_materials'))):
 mesh.set_material(i,material);assert mesh.get_material(i)==material
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='VF10_Parking_Terrain');a.static_mesh_component.set_editor_property('override_materials',[]);assert a.static_mesh_component.get_material(0)==material
assert ls.save_current_level();RESULT={'material':material.get_path_name(),'saved':True};(out/'mesh_refresh.json').write_text(json.dumps(RESULT))
