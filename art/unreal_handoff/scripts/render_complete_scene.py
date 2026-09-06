"""Capture six Unreal views in a separate editor session; never save map changes."""
import unreal,time,json,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'revision05'/'renders';OUT.mkdir(exist_ok=True)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=editor.get_editor_world()
unreal.EditorLevelLibrary.editor_set_game_view(True)
shots=[
 ('01_station_overview',[-45700,20500,11300],[-44100,18600,10250]),
 ('02_arrival_side',[-41400,16000,10800],[-43800,18500,10200]),
 ('03_gondola_front',[-44282,20750,10800],[-44282,18800,10400]),
 ('04_platform',[-42900,19400,10560],[-44280,19300,10400]),
 ('05_lower_drive',[-45400,19900,10080],[-44450,19000,10080]),
 ('07_viewing_deck',[-46350,21100,11300],[-45480,19000,10350]),
 ('08_relay_route',[-50200,21800,12400],[-47600,19100,10150]),
 ('06_terrain_context',[-49300,14700,13100],[-44200,18400,9950]),
]
state={'index':0,'phase':'position','next':time.monotonic()+20,'shots':[]}
def tick(delta):
 try:
  if time.monotonic()<state['next']:return
  i=state['index']
  if i>=len(shots):
   (OUT/'capture_report.json').write_text(json.dumps({'engine':'Unreal Engine 5.7','map':'BlockOut_R05','resolution':[2560,1440],'preview_exposure_bias_stops':0,'map_saved':False,'shots':state['shots']},indent=2))
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

