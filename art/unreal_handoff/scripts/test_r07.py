"""Capture four 1440p views using the saved R07 atmosphere."""
import unreal,time,json,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'revision07'/'ambient_renders';OUT.mkdir(exist_ok=True)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=editor.get_editor_world()
unreal.EditorLevelLibrary.editor_set_game_view(True)
shots=[
 ('01_overview',[-45700,20500,11300],[-44100,18600,10250]),
 ('02_platform_eye',[-43882,18925,10465],[-44300,19900,10420]),
 ('03_lower_deck_eye',[-44582,19125,10070],[-44200,20700,10100]),
 ('04_relay_approach',[-47182,20575,10518],[-48600,20800,10360]),
]
shots=shots[2:]
state={'index':0,'phase':'position','next':time.monotonic()+20,'shots':[]}
def tick(delta):
 try:
  if time.monotonic()<state['next']:return
  i=state['index']
  if i>=len(shots):
   (OUT/'capture_report.json').write_text(json.dumps({'engine':'Unreal Engine 5.7','map':'BlockOut_R07','resolution':[2560,1440],'preview_exposure_bias_stops':0,'map_saved':False,'shots':state['shots']},indent=2))
   unreal.unregister_slate_post_tick_callback(handle);return
  name,loc,target=shots[i]
  if state['phase']=='position':
   rotation=unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target))
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(*loc),rotation)
   state['phase']='capture';state['next']=time.monotonic()+8
  elif state['phase']=='capture':
   state['task']=unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(OUT/(name+'.png')),delay=1.0,force_game_view=True)
   state['phase']='wait';state['next']=time.monotonic()+5
  else:
   if not (OUT/(name+'.png')).exists():
    state['next']=time.monotonic()+2;return
   state['shots'].append({'name':name,'location':loc,'look_at':target})
   state['index']+=1;state['phase']='position'
 except Exception:
  (OUT/'error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)

