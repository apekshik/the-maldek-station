import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';out.mkdir(exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.editor_request_end_play()
state={'next':time.monotonic()+3,'busy':False}
def tick(dt):
 if state['busy'] or time.monotonic()<state['next'] or levels.is_in_play_in_editor():return
 state['busy']=True
 try:
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
  if world.get_name()=='BlockOut_R10':
   assert levels.save_current_level();assert levels.new_level_from_template('/Game/MaldekRefinement/R11/BlockOut_R11','/Game/MaldekRefinement/R10/BlockOut_R10')
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R11'
  (out/'started.json').write_text(json.dumps({'map':world.get_name(),'saved':True}))
 except Exception:(out/'start_error.txt').write_text(traceback.format_exc())
 unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
