"""Local R12 editor job dispatcher. No network listener; expires after four hours."""
import unreal,builtins,json,time,traceback,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'police_tape/relocation'
previous=getattr(builtins,'tape_relocation_dispatch_handle',None)
if previous:
 try:unreal.unregister_slate_post_tick_callback(previous)
 except Exception:pass
deadline=time.monotonic()+14400
state={'busy':False,'seen':set()}
def tick(dt):
 if state['busy']:return
 if time.monotonic()>deadline:
  unreal.unregister_slate_post_tick_callback(handle);return
 request=out/'request.json'
 if not request.exists():return
 state['busy']=True
 try:
  job=json.loads(request.read_text());request.unlink();key=job['id']
  if key in state['seen']:raise RuntimeError('Duplicate job ID')
  script=(out.parents[1]/'scripts'/job['script']).resolve()
  assert script.parent==(out.parents[1]/'scripts').resolve() and script.suffix=='.py'
  result=runpy.run_path(str(script),init_globals={'JOB':job})
  state['seen'].add(key)
  (out/'response.json').write_text(json.dumps({'id':key,'success':True,'report':result.get('RESULT')}))
 except Exception:(out/'response.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}))
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
builtins.tape_relocation_dispatch_handle=handle
(out/'session.json').write_text(json.dumps({'ready':True,'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'tools_available':hasattr(unreal,'StationMigrationLibrary')}))
