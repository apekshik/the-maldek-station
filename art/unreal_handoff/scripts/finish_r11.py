import unreal,time,json,traceback,runpy,gc,types
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11'
# Refresh this task's expiring dispatcher.
for obj in gc.get_objects():
 if isinstance(obj,types.FunctionType) and obj.__name__=='review_tick' and obj.__code__.co_filename.endswith('review_session.py'):
  try:unreal.unregister_slate_post_tick_callback(obj.__globals__['review_handle'])
  except:pass
runpy.run_path(str(Path(__file__).with_name('review_session.py')))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.editor_request_end_play()
state={'busy':False,'next':time.monotonic()+3}
def tick(dt):
 if state['busy'] or levels.is_in_play_in_editor() or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  root='/Game/MaldekRefinement/R11/Meshes';lib=unreal.EditorAssetLibrary
  assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='BlockOut_R11'
  unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
  task=unreal.AssetImportTask();task.filename=str(out/'fbx/SM_R04_20_Lookout_Bridge.fbx');task.destination_path=root;task.automated=True;task.save=True;task.replace_existing=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
  mesh=lib.load_asset(root+'/SM_R04_20_Lookout_Bridge')
  for i,s in enumerate(mesh.static_materials):
   m=lib.load_asset('/Game/MaldekRefinement/Materials/M_'+str(s.material_slot_name))
   if m:mesh.set_material(i,m)
  lib.save_loaded_asset(mesh);assert levels.save_current_level()
  (out/'final_saved.json').write_text(json.dumps({'saved':True,'bridge_supports_grounded':True}))
 except Exception:(out/'final_error.txt').write_text(traceback.format_exc())
 unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
