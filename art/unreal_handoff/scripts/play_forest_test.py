"""Walk the real character along the approach and capture flashlight on/off at a bend."""
import unreal,time,json,math,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Forest_Approach_Test'
assert not levels.is_in_play_in_editor();assert levels.save_current_level()
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];path=json.loads((out.parent/'revision10/approach_path.json').read_text())['points'];route=path[::4]+[path[-1]]
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2]+98)
state={'stage':'init','i':1,'start':time.monotonic(),'waypoint':time.monotonic(),'samples':[],'busy':False}
def forest_play_tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0)
  if not pawn:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);now=time.monotonic()
  if now-state['start']>150:raise RuntimeError('Playtest timeout')
  if state['stage']=='init':
   pawn.set_actor_location(wp(route[0]),False,True);state.update(stage='settle',next=now+1);return
  if state['stage']=='settle':
   if now<state['next']:return
   state.update(stage='walk',waypoint=now)
  if state['stage']=='walk':
   target=wp(route[state['i']]);here=pawn.get_actor_location();dx=target.x-here.x;dy=target.y-here.y;d=math.hypot(dx,dy)
   if abs(here.z-target.z)>75:raise RuntimeError(f'Floor mismatch at {state["i"]}: {here.z-target.z}')
   if now-state['waypoint']>12:raise RuntimeError(f'Blocked at {state["i"]}, remaining {d}')
   if d>30:
    pc.set_control_rotation(unreal.Rotator(pitch=-9,yaw=math.degrees(math.atan2(dy,dx))));pawn.add_movement_input(unreal.Vector(dx/d,dy/d,0),1,False);return
   state['samples'].append({'waypoint':state['i'],'floor_delta_cm':here.z-target.z});state['i']+=1;state['waypoint']=now
   if state['i']<len(route):return
   pawn.set_actor_location(wp(path[29]),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(path[29]),wp(path[44])));state.update(stage='on_set',next=now+3);return
  if now<state.get('next',0):return
  light=pawn.get_components_by_class(unreal.SpotLightComponent)[0]
  if state['stage']=='on_set':
   light.set_visibility(True);state.update(stage='on',next=now+3)
  elif state['stage']=='on':
   light.set_visibility(True);unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(out/'play_flashlight_on.png'));state.update(stage='off_set',next=now+3)
  elif state['stage']=='off_set':light.set_visibility(False);state.update(stage='off',next=now+3)
  elif state['stage']=='off':
   unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(out/'play_flashlight_off.png'));state.update(stage='done',next=now+3)
  elif state['stage']=='done':
   light.set_visibility(True);state['success']=True;state['duration_seconds']=now-state['start'];(out/'play_validation.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(forest_play_handle)
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();(out/'play_validation.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(forest_play_handle)
 finally:state['busy']=False
forest_play_handle=unreal.register_slate_post_tick_callback(forest_play_tick);levels.editor_request_begin_play()

