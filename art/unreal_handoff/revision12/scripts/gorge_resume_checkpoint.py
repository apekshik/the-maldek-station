"""Save the latest door/audio state before the bounded landscape tool build."""
import unreal,json,shutil,time
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if ls.is_in_play_in_editor():ls.editor_request_end_play()
def finish(dt):
 if ls.is_in_play_in_editor():return
 unreal.unregister_slate_post_tick_callback(handle)
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
 assert ls.save_current_level()
 backup=out/'Station_R12_ca7d494_before_resume.umap';assert not backup.exists()
 shutil.copy2(b.parents[2]/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 (out/'preserve_resume.json').write_text(json.dumps({a.get_actor_label():str(a.get_actor_transform()) for a in actors},indent=2))
 (out/'resume_checkpoint.json').write_text(json.dumps({'saved':True,'backup':str(backup),'actors':len(actors)}))
 unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(finish)
