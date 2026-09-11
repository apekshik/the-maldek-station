import runpy,traceback,unreal,time
from pathlib import Path
base=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff')
deadline=time.monotonic()+12
def start(dt):
 if time.monotonic()<deadline:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  runpy.run_path(str(base/'revision12/scripts/police_tape_install.py'))
  (base/'revision12/police_tape/install_error.txt').unlink(missing_ok=True)
 except Exception:(base/'revision12/police_tape/install_error.txt').write_text(traceback.format_exc())
 runpy.run_path(str(base/'scripts/r12_session.py'))
handle=unreal.register_slate_post_tick_callback(start)
