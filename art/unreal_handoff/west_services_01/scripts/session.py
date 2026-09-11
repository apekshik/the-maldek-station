import unreal,builtins,json,time,traceback,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
old=getattr(builtins,'west_dispatch',None)
if old:unreal.unregister_slate_post_tick_callback(old)
state={'busy':False}
def tick(dt):
 if state['busy']:return
 p=OUT/'request.json'
 if not p.exists():return
 state['busy']=True;j={}
 try:
  j=json.loads(p.read_text());p.unlink();f=(OUT/'scripts'/j['script']).resolve();assert f.parent==(OUT/'scripts').resolve() and f.suffix=='.py'
  result=runpy.run_path(str(f),init_globals={'JOB':j});(OUT/'response.json').write_text(json.dumps({'id':j['id'],'success':True,'report':result.get('RESULT')},default=str))
 except Exception:(OUT/'response.json').write_text(json.dumps({'id':j.get('id'),'success':False,'error':traceback.format_exc()}))
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);builtins.west_dispatch=handle
RESULT={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'ready':True}
(OUT/'session.json').write_text(json.dumps(RESULT))
