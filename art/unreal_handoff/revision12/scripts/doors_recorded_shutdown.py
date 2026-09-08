"""Save the current editor session before rebuilding the door audio components."""
import unreal,time,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
out=Path(__file__).resolve().parents[1]/'doors'/'recorded_audio';out.mkdir(parents=True,exist_ok=True)
deadline=time.monotonic()+30
if ls.is_in_play_in_editor():ls.editor_request_end_play()
def finish(dt):
 if ls.is_in_play_in_editor() and time.monotonic()<deadline:return
 unreal.unregister_slate_post_tick_callback(handle)
 assert not ls.is_in_play_in_editor()
 assert unreal.EditorLoadingSavingUtils.save_dirty_packages(True,True)
 (out/'shutdown.json').write_text(json.dumps({'saved':True}))
 unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(finish)
RESULT={'shutdown_queued':True}
