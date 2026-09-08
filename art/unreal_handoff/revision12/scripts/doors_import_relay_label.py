import unreal,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';root='/Game/MaldekRefinement/R12/Doors';lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
row=json.loads((out/'relay_leaf_manifest.json').read_text())['chunks'][0];file=out/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=lib.load_asset(root+'/Meshes/'+row['name']);assert mesh
original=lib.load_asset(root+'/Meshes/SM_StationDoor_Leaf');mats={str(s.material_slot_name):s.material_interface for s in original.static_materials}
for i,s in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(s.material_slot_name)])
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);sm.remove_collisions(mesh);ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True)
a=mesh.get_bounding_box();b=original.get_bounding_box();err=max(abs(x-y) for p,q in [(a.min,b.min),(a.max,b.max)] for x,y in zip(p.to_tuple(),q.to_tuple()));assert err<.02
assert lib.save_loaded_asset(mesh)
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if actor.get_actor_label().startswith('R12_Door_Relay_'):actor.leaf.set_static_mesh(mesh)
assert ls.save_current_level()
RESULT={'success':True,'bounds_difference_cm':err,'collision_unchanged':True};(out/'relay_label_import.json').write_text(json.dumps(RESULT,indent=2))
