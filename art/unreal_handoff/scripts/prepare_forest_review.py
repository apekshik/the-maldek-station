import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];path=json.loads((out.parent/'revision10/approach_path.json').read_text())['points']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2]+98)
state={'stage':0,'next':time.monotonic(),'busy':False}
def forest_ready_tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0)
  if not pawn:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);c=pawn.get_components_by_class(unreal.SpotLightComponent)[0]
  if state['stage']==0:
   pawn.set_actor_location(wp(path[24]),False,True);r=unreal.MathLibrary.find_look_at_rotation(wp(path[24]),wp(path[40]));r.pitch=-6;pc.set_control_rotation(r);c.set_visibility(True);state.update(stage=1,next=time.monotonic()+4)
  elif state['stage']==1:
   unreal.SystemLibrary.execute_console_command(w,'HighResShot 1600x900 filename='+str(out/'gameplay_on.png').replace('\\','/'));state.update(stage=2,next=time.monotonic()+4)
  elif state['stage']==2:c.set_visibility(False);state.update(stage=3,next=time.monotonic()+4)
  elif state['stage']==3:
   unreal.SystemLibrary.execute_console_command(w,'HighResShot 1600x900 filename='+str(out/'gameplay_off.png').replace('\\','/'));state.update(stage=4,next=time.monotonic()+4)
  else:
   c.set_visibility(True);(out/'ready.json').write_text(json.dumps({'pawn':pawn.get_class().get_name(),'light_intensity':c.intensity,'light_radius':c.attenuation_radius,'light_visible':c.is_visible(),'map':'Forest_Approach_Test','playing':True},indent=2));unreal.unregister_slate_post_tick_callback(forest_ready_handle)
 except Exception:
  (out/'ready_error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(forest_ready_handle)
 finally:state['busy']=False
forest_ready_handle=unreal.register_slate_post_tick_callback(forest_ready_tick)
if not levels.is_in_play_in_editor():levels.editor_request_begin_play()
