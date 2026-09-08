import unreal,runpy,json,traceback,time
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if ls.is_in_play_in_editor():ls.editor_request_end_play()
if JOB.get('apply_and_capture'):
 b=Path(__file__).resolve().parents[1];deadline=time.monotonic()+30
 def finish_when_stopped(dt):
  if ls.is_in_play_in_editor() and time.monotonic()<deadline:return
  unreal.unregister_slate_post_tick_callback(handle)
  try:
   runpy.run_path(str(b/'scripts/fog_density_pass.py'),init_globals={'JOB':{'apply':True}})
   runpy.run_path(str(b/'scripts/fog_density_capture.py'),init_globals={'JOB':{'shots':[
    ['forest',[-25,-28,1.7],[-15,-16,5]],['bridge',[16,17,5.4],[12,7.5,7]]
   ]}})
  except Exception:
   (b/'fog_density'/'error.json').write_text(json.dumps({'error':traceback.format_exc()}))
 handle=unreal.register_slate_post_tick_callback(finish_when_stopped)
RESULT={'ending_preview':True}
