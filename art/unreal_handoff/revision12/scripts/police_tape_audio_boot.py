import unreal,time,runpy,traceback
from pathlib import Path
b=Path(__file__).resolve().parent;deadline=time.monotonic()+12
def tick(dt):
 if time.monotonic()<deadline:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:runpy.run_path(str(b/'police_tape_audio_install.py'))
 except Exception:(b.parent/'police_tape/audio_install_error.txt').write_text(traceback.format_exc())
 runpy.run_path(str(b/'police_tape_relocation_session.py'))
handle=unreal.register_slate_post_tick_callback(tick)
