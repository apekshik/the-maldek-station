"""Temporary local review dispatcher. Expires after 30 minutes; no network listener."""
import unreal,json,time,traceback,runpy
from pathlib import Path
review_out=Path(__file__).resolve().parents[1]
review_deadline=time.monotonic()+1800
def review_tick(delta):
 if time.monotonic()>review_deadline:
  unreal.unregister_slate_post_tick_callback(review_handle);return
 request=review_out/'review_request.json'
 if not request.exists():return
 try:
  command=json.loads(request.read_text());request.unlink()
  action=command['action'];result={}
  if action=='camera':
   r=command['rotation'];unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(*command['location']),unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
  elif action=='script':
   script=(review_out/'scripts'/command['name']).resolve()
   assert script.parent==(review_out/'scripts').resolve() and script.suffix=='.py'
   runpy.run_path(str(script))
  elif action=='console':
   unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),command['command'])
  elif action=='stop':unreal.unregister_slate_post_tick_callback(review_handle)
  (review_out/'review_response.json').write_text(json.dumps({'action':action,'success':True,'result':result}))
 except Exception:
  (review_out/'review_response.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}))
review_handle=unreal.register_slate_post_tick_callback(review_tick)
