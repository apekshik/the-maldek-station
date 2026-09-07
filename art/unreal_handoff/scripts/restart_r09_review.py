"""Return the tested map to a fresh Play session without test-only route overrides."""
import unreal,time,json
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
out=Path(__file__).resolve().parents[1]/'revision09'
unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/'boarding_play.png'))
state={'start':time.monotonic(),'stopping':False}
def tick(dt):
 if time.monotonic()-state['start']<3:return
 if not state['stopping']:
  levels.editor_request_end_play();state['stopping']=True;return
 if levels.is_in_play_in_editor():return
 assert levels.save_current_level()
 unreal.unregister_slate_post_tick_callback(handle)
 levels.editor_request_begin_play()
 (out/'review_ready.json').write_text(json.dumps({'map':'/Game/MaldekRefinement/R09/BlockOut_R09','fresh_play_requested':True}))
handle=unreal.register_slate_post_tick_callback(tick)
