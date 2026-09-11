import unreal,json,time
from pathlib import Path
out=Path(__file__).resolve().parents[1]
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ls.editor_request_end_play()
state={'frames':0}
def finish(dt):
 state['frames']+=1
 if state['frames']<10 or ls.is_in_play_in_editor():return
 unreal.unregister_slate_post_tick_callback(handle)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()
 saved=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'peek_restart.json').write_text(json.dumps({'world':world,'saved':saved}))
 if saved:unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(finish)
RESULT={'closing_after_save':True}
