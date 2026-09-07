import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not levels.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R10'
world.get_world_settings().set_editor_property('kill_z',0.)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
# Move the distant marker onto the mountain slope 1.4km away.
for a in aa:
 if a.get_actor_label().startswith('R10_Distant_'):
  p=a.get_actor_location();p.y+=75000;p.z+=32227.830254-7581.472909;a.set_actor_location(p,False,False)
  if 'Window' in a.get_actor_label():a.set_actor_scale3d(unreal.Vector(2.2,.04,1.1))
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(out/'restart_checkpoint.json').write_text(json.dumps({'saved':True,'map':world.get_name()}))
unreal.SystemLibrary.quit_editor()
