import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
root='/Game/MaldekRefinement/PassengerLodge/Ground';unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(OUT/'fbx/SM_Lodge_Site_Ground.fbx');t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;t.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset(root+'/SM_Lodge_Site_Ground');assert mesh
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='VF10_Parking_Terrain')
c=a.static_mesh_component;old=c.static_mesh;assert old.get_path_name() in ['/Game/MaldekRefinement/R12/Gorge/Meshes/SM_Station_Gorge_Terrain.SM_Station_Gorge_Terrain',root+'/SM_Lodge_Site_Ground.SM_Lodge_Site_Ground']
old_bounds=old.get_bounds();new_bounds=mesh.get_bounds();assert (old_bounds.origin-new_bounds.origin).length()<.2 and (old_bounds.box_extent-new_bounds.box_extent).length()<.2
for i in range(len(mesh.static_materials)):mesh.set_material(i,c.get_material(min(i,len(old.static_materials)-1)))
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
unreal.EditorAssetLibrary.save_loaded_asset(mesh);c.set_static_mesh(mesh)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
RESULT={'new_mesh':mesh.get_path_name(),'original_mesh_preserved':True};(OUT/'ground_install.json').write_text(json.dumps(RESULT,indent=2))
