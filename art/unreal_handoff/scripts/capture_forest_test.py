import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';out.mkdir(exist_ok=True)
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();prefix='after' if world.get_name()=='Forest_Approach_Test' else 'before'
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
shots=[('parking',(-36,-58.8,.65),(-29,-53,.5)),('bend',(-31.7,-46.4,.9),(-26,-37,.9)),('overview',(-48,-50,15),(-25,-36,0))]
state={'i':0,'stage':0,'next':time.monotonic()+2}
def forest_capture_tick(dt):
 if state.get('busy') or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  if state['i']==len(shots):
   (out/(prefix+'_captures.json')).write_text(json.dumps(shots));unreal.unregister_slate_post_tick_callback(forest_capture_handle);return
  name,p,q=shots[state['i']]
  if state['stage']==0:
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)));state.update(stage=1,next=time.monotonic()+6)
  else:
   unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(out/(prefix+'_'+name+'.png')),force_game_view=True);state.update(stage=0,i=state['i']+1,next=time.monotonic()+4)
 except Exception:
  (out/'capture_error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(forest_capture_handle)
 finally:state['busy']=False
forest_capture_handle=unreal.register_slate_post_tick_callback(forest_capture_tick)

