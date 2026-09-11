import unreal,runpy,time,traceback
from pathlib import Path
b=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff');end=time.monotonic()+10
def go(dt):
 if time.monotonic()<end:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  runpy.run_path(str(b/'revision12/scripts/police_tape_finish.py'))
  runpy.run_path(str(b/'revision12/scripts/police_tape_verify.py'))
 except Exception:(b/'revision12/police_tape/verify_error.txt').write_text(traceback.format_exc())
 runpy.run_path(str(b/'scripts/r12_session.py'))
handle=unreal.register_slate_post_tick_callback(go)
