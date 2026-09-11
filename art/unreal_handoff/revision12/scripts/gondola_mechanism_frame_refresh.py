import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'gondola_mechanism';root='/Game/MaldekRefinement/R12/GondolaMechanism';oldroot='/Game/MaldekRefinement/R12/GondolaRoute'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
plan=json.loads((b/'gondola_route/plan.json').read_text());rows=json.loads((out/'exports.json').read_text());pylons=json.loads((out/'pylons.json').read_text());shell=json.loads((out/'lower_shell.json').read_text())
meshes={}
for row in [r for r in rows if r['name']=='SM_GM_Millford_Frame']:
 name=row['name'];t=unreal.AssetImportTask();t.filename=str(out/'fbx'/(name+'.fbx'));t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;t.options=opt;at.import_asset_tasks([t]);mesh=lib.load_asset(root+'/Meshes/'+name);assert mesh
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  key=str(slot.get_editor_property('imported_material_slot_name'));mat=lib.load_asset(oldroot+'/Materials/M_'+key) if key.startswith('Pylon_') else lib.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_'+key)
  assert mat,(name,key);mesh.set_material(i,mat)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 if name=='SM_GM_Continuous_Rope':
  settings=sms.get_lod_build_settings(mesh,0);settings.set_editor_property('use_full_precision_u_vs',True);sms.set_lod_build_settings(mesh,0,settings)
 lib.save_loaded_asset(mesh);meshes[name]=mesh

assert ls.save_current_level();RESULT={'frame_supports_updated':True}
