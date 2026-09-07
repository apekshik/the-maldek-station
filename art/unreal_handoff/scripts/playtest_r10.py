"""Exercise real character collision across both newly opened dock connections."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level();assert levels.load_level('/Game/MaldekRefinement/R10/BlockOut_R10')
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
state={'stage':0,'next':time.monotonic(),'results':[],'deadline':time.monotonic()+65}
def tick(dt):
 try:
  if time.monotonic()>state['deadline']:raise RuntimeError('Play test timed out')
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  pawn=unreal.GameplayStatics.get_player_pawn(world,0)
  if not pawn:return
  pc=unreal.GameplayStatics.get_player_controller(world,0);now=time.monotonic()
  if state['stage']==0:
   state['pawn']=pawn.get_class().get_path_name();assert '/R10/' in state['pawn']
   state['spawn']=[pawn.get_actor_location().x,pawn.get_actor_location().y,pawn.get_actor_location().z]
   light=pawn.get_components_by_class(unreal.SpotLightComponent)[0];state['light_function']=str(light.get_editor_property('light_function_material'));assert 'M_Flashlight_Optics' in state['light_function']
   state['beam_visible']=light.is_visible();state['wind']=[{'name':a.get_actor_label(),'playing':a.audio_component.is_playing()} for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.AmbientSound)]
   pawn.set_actor_location(unreal.Vector(origin[0]+290,origin[1]+630,origin[2]+500),False,True);state.update(stage=1,next=now+1);return
  if state['stage'] in [1,3]:
   if now<state['next']:return
   state['from']=[pawn.get_actor_location().x,pawn.get_actor_location().y,pawn.get_actor_location().z];state.update(stage=state['stage']+1,next=now+1.2);return
  if state['stage'] in [2,4]:
   if now<state['next']:pawn.add_movement_input(unreal.Vector(0,1,0),1,False);return
   p=pawn.get_actor_location();r={'side':'west' if state['stage']==2 else 'east','delta_y_cm':p.y-state['from'][1],'end_z':p.z};state['results'].append(r);assert r['delta_y_cm']>240,r
   assert abs(p.z-(origin[2]+496))<35,p.z
   if state['stage']==2:
    pawn.set_actor_location(unreal.Vector(origin[0]-270,origin[1]+770,origin[2]+500),False,True);state.update(stage=3,next=now+1);return
   # Place the player facing concrete for the F-key and beam appearance check.
   pawn.set_actor_location(unreal.Vector(-44160,18780,10395),False,True);pc.set_control_rotation(unreal.Rotator(pitch=-4,yaw=-90));state.update(stage=5,next=now+3);return
  if state['stage']==5 and now>state['next']:
   state['success']=True;(out/'play_verification.json').write_text(json.dumps(state,indent=2));unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/'flashlight_on.png'));unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();(out/'play_verification.json').write_text(json.dumps(state,indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
