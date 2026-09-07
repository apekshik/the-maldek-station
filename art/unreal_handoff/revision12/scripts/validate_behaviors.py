"""Exercise inherited flashlight input, footstep suppression and live ambience in PIE."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
state={'phase':'start','next':time.monotonic()+10,'busy':False,'checks':{},'deadline':time.monotonic()+90}
def finish():
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 state['success']='error' not in state and all(state['checks'].values());state['phase']='finished'
 (b/JOB.get('report','behavior_validation.json')).write_text(json.dumps(state,indent=2));ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic();assert now<state['deadline']
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  foot=p.get_component_by_class(unreal.SurfaceFootstepComponent);beam=p.get_component_by_class(unreal.SpotLightComponent)
  assert foot and beam
  if state['phase']=='start':
   state['initial_flashlight']=beam.is_visible();state['surface_audio_sets']={name:[s.get_path_name() for s in foot.get_editor_property(name) if s] for name in ['soil_steps','gravel_steps','metal_steps','concrete_steps','wood_steps']}
   state['checks']['five_audio_sets_present']=all(state['surface_audio_sets'].values())
   state['ambience']=[{'actor':a.get_actor_label(),'sound':c.sound.get_path_name() if c.sound else None,'playing':c.is_playing()} for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) for c in a.get_components_by_class(unreal.AudioComponent)]
   state['checks']['ambience_playing']=any(r['playing'] and r['sound'] for r in state['ambience'])
   state['input_dispatched']=unreal.StationMigrationLibrary.send_pie_key('F',True);state.update(phase='toggle1',next=now+.4);return
  if state['phase']=='toggle1':
   state['checks']['flashlight_first_toggle']=beam.is_visible()!=state['initial_flashlight'];unreal.StationMigrationLibrary.send_pie_key('F',False);state.update(phase='press2',next=now+.3);return
  if state['phase']=='press2':
   unreal.StationMigrationLibrary.send_pie_key('F',True);state.update(phase='toggle2',next=now+.4);return
  if state['phase']=='toggle2':
   state['checks']['flashlight_second_toggle']=beam.is_visible()==state['initial_flashlight'];unreal.StationMigrationLibrary.send_pie_key('F',False)
   p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(o[0]+2100,o[1],o[2]+500),False,True)
   state.update(phase='settle',next=now+2);return
  if state['phase']=='settle':
   assert not p.character_movement.is_falling();state['idle_start']=foot.footstep_count;state.update(phase='idle',next=now+3);return
  if state['phase']=='idle':
   state['idle_end']=foot.footstep_count;state['checks']['idle_silent']=state['idle_start']==state['idle_end']
   pos=p.get_actor_location();pos.z+=200;p.set_actor_location(pos,False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FALLING)
   state['airborne_test']='Controlled 2 m drop solely for suppression test; ordinary walking routes use no drops or teleports.';state.update(phase='await_air',next=now+.05);return
  if state['phase']=='await_air':
   assert p.character_movement.is_falling(),'Jump did not enter falling state'
   state['air_start']=foot.footstep_count;state['air_samples']=[];state.update(phase='air',next=now);return
  if state['phase']=='air':
   if p.character_movement.is_falling():
    state['air_samples'].append(foot.footstep_count);p.add_movement_input(unreal.Vector(1,0,0),.5,False);return
   state['checks']['airborne_silent']=bool(state['air_samples']) and all(n==state['air_start'] for n in state['air_samples']);p.stop_jumping();finish()
 except Exception:state['error']=traceback.format_exc();finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
