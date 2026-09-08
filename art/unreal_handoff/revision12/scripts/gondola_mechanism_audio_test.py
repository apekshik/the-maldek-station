"""Record real spatial output: opposite listener sides, distant silence, full machine and dock."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_mechanism'/'audio_final';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
s={'phase':'warm','next':time.monotonic()+32,'deadline':time.monotonic()+115,'checks':[],'clips':[],'index':0}
def finish(error=None):
 unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(False)
 s['error']=error;s['passed']=error is None
 (out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
def tick(dt):
 if time.monotonic()<s['next']:return
 try:
  assert time.monotonic()<s['deadline'],'Audio test timed out'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  capture_state=unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(True)
  if 'capture_override' not in s:s['capture_override']=dict(capture_state)
  pc=unreal.GameplayStatics.get_player_controller(w,0);allactors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor);actors={a.get_actor_label():a for a in allactors};m=actors['R12_Gondola_Mechanism'];g=m.gondola;motor=actors['R12_GM_Audio_Motor'];wheel=actors['R12_GM_Audio_Bullwheel_0']
  if s['phase']=='warm':
   assert not g.is_moving() and abs(g.get_route_distance()-3048)<1,'Staging changed before audio test'
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True)
   for a in allactors:
    if a.get_actor_label().startswith('R12_GM_Audio_'):continue
    if isinstance(a,unreal.StationCableAudio):a.set_actor_tick_enabled(False)
    for c in a.get_components_by_class(unreal.AudioComponent):c.stop();c.set_volume_multiplier(0)
   s['full_gain_test_cruise_cm_s']=80;g.cruise_speed=80;g.begin_arrival();s.update(phase='place',next=time.monotonic()+.1)
  elif s['phase']=='place':
   entries=[('motor_right',motor.get_actor_location()+unreal.Vector(400,0,0),False),('motor_left',motor.get_actor_location()+unreal.Vector(-400,0,0),False),('motor_far',motor.get_actor_location()+unreal.Vector(20000,0,0),False),('full_drive',wheel.get_actor_location()+unreal.Vector(0,-350,-150),True)]
   name,eye,full=entries[s['index']]
   for source in m.sound_sources:
    source.running_volume=2. if source.actor==motor else (3. if full and 'Bullwheel' in source.actor.get_actor_label() else 1. if full else 0)
   # Struct array changes require writing the complete copied array back.
   values=list(m.sound_sources)
   for source in values:source.running_volume=2. if source.actor==motor else (3. if full and 'Bullwheel' in source.actor.get_actor_label() else 1. if full else 0)
   m.sound_sources=values
   p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=90,roll=0));s.update(name=name,phase='record',next=time.monotonic()+1)
  elif s['phase']=='record':
   assert g.is_moving();assert motor.get_component_by_class(unreal.AudioComponent).is_playing()
   unreal.AudioMixerLibrary.start_recording_output(w,3);s.update(phase='save',next=time.monotonic()+3)
  elif s['phase']=='save':
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,s['name'],str(out));s['clips'].append(s['name']+'.wav');s['index']+=1;s.update(phase='place' if s['index']<4 else 'dock',next=time.monotonic()+.5)
  elif s['phase']=='dock':
   if not g.is_docked():s['next']=time.monotonic()+.3;return
   p.set_actor_location(motor.get_actor_location()-unreal.Vector(0,250,64),False,True);s.update(phase='parked',next=time.monotonic()+2)
  elif s['phase']=='parked':
   assert all(not a.actor.get_component_by_class(unreal.AudioComponent).is_playing() for a in m.sound_sources);s['checks'].append('All nine motion loops stop at dock')
   unreal.AudioMixerLibrary.start_recording_output(w,2);s.update(phase='end',next=time.monotonic()+2)
  else:
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'parked',str(out));s['clips'].append('parked.wav');s['checks']+=['Motor loop active during travel','Real listener moved to opposite sides and 200 metres away'];finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
