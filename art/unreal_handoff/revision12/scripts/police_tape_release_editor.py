import unreal,runpy,builtins,os
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();b=Path(__file__).resolve().parents[1]
runpy.run_path(str(b.parent/'scripts/r12_session.py'))
h=getattr(builtins,'tape_relocation_dispatch_handle',None)
if h:unreal.unregister_slate_post_tick_callback(h);builtins.tape_relocation_dispatch_handle=None
RESULT={'pid':os.getpid(),'idle':True,'r12_dispatcher_ready':True}
