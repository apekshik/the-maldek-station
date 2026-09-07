"""Save the complete active editor baseline before any R12 migration."""
import unreal,json,time,traceback,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[2]/'checkpoints/pre_vf07'
checkpoint_scripts=Path(__file__).resolve().parent
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.editor_request_end_play()
deadline=time.monotonic()+2
def checkpoint_tick(dt):
 if levels.is_in_play_in_editor() or time.monotonic()<deadline:return
 try:
  assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
  assert levels.save_current_level()
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
  actors=[]
  for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
   row={'path':a.get_path_name(),'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'transform':str(a.get_actor_transform()),'parent':str(a.get_attach_parent_actor()),'components':[]}
   for c in a.get_components_by_class(unreal.StaticMeshComponent):
    row['components'].append({'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[m.get_path_name() if m else None for m in c.get_materials()],'collision':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'transform':str(c.get_world_transform())})
   actors.append(row)
  (out/'unreal_saved.json').write_text(json.dumps({'world':world.get_path_name(),'saved':True,'actors':actors},indent=2))
  runpy.run_path(str(checkpoint_scripts/'review_session.py'))
  (out/'unreal_error.txt').unlink(missing_ok=True)
 except Exception:(out/'unreal_error.txt').write_text(traceback.format_exc())
 unreal.unregister_slate_post_tick_callback(checkpoint_handle)
checkpoint_handle=unreal.register_slate_post_tick_callback(checkpoint_tick)
