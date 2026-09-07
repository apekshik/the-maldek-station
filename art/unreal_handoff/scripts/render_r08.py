"""Capture three 1440p views of the saved R08 wall lights."""
import unreal,time,json,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'revision08'/'final_renders';OUT.mkdir(exist_ok=True)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=editor.get_editor_world()
unreal.EditorLevelLibrary.editor_set_game_view(True)
shots=[
 ('01_overview',[-45700,20500,11300],[-44100,18600,10250]),
 ('02_control_entry',[-44400,18700,10465],[-43860,18488,10490]),
 ('03_waiting_hall_entry',[-43550,18780,10465],[-43132,18490,10500]),
]
state={'index':0,'phase':'position','next':time.monotonic()+20,'shots':[]}
def tick(delta):
 try:
  if time.monotonic()<state['next']:return
  i=state['index']
  if i>=len(shots):
   (OUT/'capture_report.json').write_text(json.dumps({'engine':'Unreal Engine 5.7','map':'BlockOut_R08','resolution':[2560,1440],'preview_exposure_bias_stops':0,'map_saved':False,'shots':state['shots']},indent=2))
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
