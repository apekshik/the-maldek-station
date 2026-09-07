import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.editor_request_end_play()
state={'busy':False,'next':time.monotonic()+2}
def tick(dt):
 if state['busy'] or levels.is_in_play_in_editor() or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  code=Path(__file__).with_name('import_r10.py').read_text().replace("'revision10'","'revision11'").replace('/R10','/R11').replace('BlockOut_R10','BlockOut_R11').replace("f.stem.startswith('SM_R10_')","f.stem.startswith('SM_R11_')").replace("'Canyon_Terrain' in f.stem","f.stem=='SM_R11_Terrain'")
  exec(compile(code,'import_r11_assets','exec'),{'__file__':__file__})
  (out/'import_complete.json').write_text(json.dumps({'saved':True}))
 except Exception:(out/'import_error.txt').write_text(traceback.format_exc())
 unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
