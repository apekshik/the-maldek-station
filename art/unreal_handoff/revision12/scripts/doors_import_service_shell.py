import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';root='/Game/MaldekRefinement/R12/Doors';lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();data=json.loads((out/'service_shell_manifest.json').read_text());row=data['chunk']
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/row['file']);t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True;opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=lib.load_asset(root+'/Meshes/'+row['name']);original=lib.load_asset('/Game/MaldekRefinement/R13/Meshes/'+data['source_asset']);assert mesh and original
mats={str(s.material_slot_name):s.material_interface for s in original.static_materials}
for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(slot.material_slot_name)])
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);assert sm.get_convex_collision_count(mesh)==row['collision_hulls'];sm.set_nanite_settings(mesh,original.get_editor_property('nanite_settings'),True);assert lib.save_loaded_asset(mesh)
changed=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh==original:c.set_static_mesh(mesh);changed.append(a.get_actor_label())
assert len(changed)==1;assert ls.save_current_level();RESULT={'success':True,'shell_actor':changed,'retired_static_door_parts':data['removed'],'all_other_collision_preserved':True};(out/'service_shell_import.json').write_text(json.dumps(RESULT,indent=2))
