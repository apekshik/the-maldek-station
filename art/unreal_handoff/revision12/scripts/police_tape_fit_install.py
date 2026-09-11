import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';rows=json.loads((out/'wrap_fit/fitted.json').read_text());aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary;assert not ls.is_in_play_in_editor();actors={a.get_actor_label():a for a in aa.get_all_level_actors()};root='/Game/MaldekRefinement/R12/PoliceTape';m=lib.load_asset(root+'/M_PoliceTape');w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
for r in rows:
 name='SM_'+r['wrap'];path=root+'/Wraps/'+name
 if True:
  t=unreal.AssetImportTask();t.filename=r['fitted_fbx'];t.destination_path=root+'/Wraps';t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;t.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
 mesh=lib.load_asset(path);assert mesh;mesh.set_material(0,m);lib.save_loaded_asset(mesh);a=actors[r['wrap']];a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(1,1,1));a.set_actor_rotation(unreal.Rotator(pitch=r['tree_rotation'][0],yaw=r['tree_rotation'][1],roll=r['tree_rotation'][2]),False)
assert ls.save_current_level();RESULT={'fitted_wraps':len(rows),'saved':True};(out/'wrap_fit/installed.json').write_text(json.dumps(RESULT))

