import unreal,json,time,runpy,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
deadline=time.monotonic()+8
def finish(dt):
 if time.monotonic()<deadline:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:report=runpy.run_path(str(b/'scripts'/'platform_refine_verify.py'))['RESULT']
 except Exception:report={'passed':False,'error':traceback.format_exc()}
 (b/'platform_refine'/'reopen_verification.json').write_text(json.dumps(report,indent=2))
handle=unreal.register_slate_post_tick_callback(finish);RESULT={'reopened':True}
