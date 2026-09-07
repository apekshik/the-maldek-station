import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10'/'final_renders';out.mkdir(exist_ok=True)
shots=[('01_dock_patch',[-44720,18850,10650],[-44480,19350,10300]),('02_stair_patch',[-45160,18850,10470],[-44950,18650,10200]),('03_canyon',[-43992,19475,10465],[-44282,24000,9600]),('04_forest_approach',[-40682,12625,9970],[-41300,13500,9890]),('05_ticket_hall',[-42500,18580,10650],[-42900,18100,10450])]
state={'i':0,'stage':0,'next':time.monotonic()+5}
def tick(dt):
 try:
  if time.monotonic()<state['next']:return
  if state['i']>=len(shots):
   (out/'complete.json').write_text(json.dumps(shots));unreal.unregister_slate_post_tick_callback(handle);return
  name,p,t=shots[state['i']]
  if state['stage']==0:
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(*p),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*p),unreal.Vector(*t)));state.update(stage=1,next=time.monotonic()+6)
  elif state['stage']==1:
   unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(name+'.png')),force_game_view=True);state.update(stage=2,next=time.monotonic()+6)
  else:
   if not (out/(name+'.png')).exists():
    state.update(stage=1,next=time.monotonic()+3);return
   state.update(stage=0,i=state['i']+1,next=time.monotonic()+2)
 except Exception:
  (out/'error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
