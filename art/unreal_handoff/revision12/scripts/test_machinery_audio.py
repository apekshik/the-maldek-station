"""PIE source, attenuation, recorded output, click and moving-cable checks."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'machinery_audio'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'checks':[],'deadline':time.monotonic()+150}
def check(name,value):
 assert value,name
 s['checks'].append(name)
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 (out/'runtime.json').write_text(json.dumps({'success':error is None,'checks':s['checks'],'error':error},indent=2))
 unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 try:
  assert time.monotonic()<s['deadline'],'Timed out'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  opening=p.get_component_by_class(unreal.StationOpeningComponent);t=opening.elapsed
  if t<36:return # let the title cue finish before isolated machinery captures
  actors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)
  cable=next(a for a in actors if isinstance(a,unreal.StationCableAudio))
  loops={a.get_actor_label().replace('R12_Audio_',''):a for a in actors if a.get_actor_label() in ['R12_Audio_Generator','R12_Audio_Flywheel','R12_Audio_Ventilation']}
  def record():unreal.AudioMixerLibrary.start_recording_output(w,5)
  def stop(name):unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,name,str(out))
  def isolate(name):
   for a in actors:
    for c in a.get_components_by_class(unreal.AudioComponent):c.stop()
   a=loops[name];c=a.get_component_by_class(unreal.AudioComponent);c.play()
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   p.set_actor_location(a.get_actor_location()+unreal.Vector(280,0,0),False,True)
  if s['phase']==0:
   check('three fixed sources present',len(loops)==3)
   for name,a in loops.items():
    c=a.get_component_by_class(unreal.AudioComponent);atten=c.get_editor_property('attenuation_overrides')
    check(name+' loop playing',c.is_playing() and c.sound.get_editor_property('looping'))
    check(name+' positional and wall occlusion',atten.spatialize and atten.attenuate and atten.enable_occlusion)
   check('flashlight click multiplier increased',opening.switch_volume==1.)
   check('cable targets moving system',isinstance(cable.gondola_target,unreal.GondolaSystem))
   cable.set_actor_tick_enabled(False);cable.audio.stop()
   isolate('Generator');s.update(phase=1,next=t+1)
  elif t<s['next']:return
  elif s['phase']==1:record();s.update(phase=2,next=t+2)
  elif s['phase']==2:
   stop('generator_near');p.set_actor_location(loops['Generator'].get_actor_location()+unreal.Vector(5000,0,0),False,True);s.update(phase=3,next=t+1)
  elif s['phase']==3:record();s.update(phase=4,next=t+2)
  elif s['phase']==4:stop('generator_far');isolate('Flywheel');s.update(phase=5,next=t+1)
  elif s['phase']==5:record();s.update(phase=6,next=t+2)
  elif s['phase']==6:stop('flywheel_near');isolate('Ventilation');s.update(phase=7,next=t+1)
  elif s['phase']==7:record();s.update(phase=8,next=t+2)
  elif s['phase']==8:
   stop('ventilation_near')
   for a in loops.values():a.get_component_by_class(unreal.AudioComponent).stop()
   record();p.toggle_flashlight();s.update(phase=9,next=t+.7)
  elif s['phase']==9:p.toggle_flashlight();s.update(phase=10,next=t+.7)
  elif s['phase']==10:
   stop('flashlight_clicks');check('both real toggles played',opening.switch_count==2)
   # Isolate motion detection from the live cabin's existing departure schedule.
   g=cable.gondola_target;g.set_actor_tick_enabled(False)
   cable.set_actor_tick_enabled(True)
   mesh=g.get_component_by_class(unreal.StaticMeshComponent);s['test_mesh']=mesh
   s['mesh_position']=mesh.get_world_location();s.update(phase=11,next=t+3)
  elif s['phase']==11:
   check('stationary cabin fades cable to silence',cable.motion_amount<.01 and not cable.audio.is_playing())
   p.set_actor_location(s['mesh_position']+unreal.Vector(300,0,100),False,True)
   record();s.update(phase=12,next=t+2)
  elif s['phase']==12:
   check('moving gondola activates cable',cable.motion_amount>.1 and cable.audio.is_playing())
   stop('cable_moving');s.update(phase=13,next=t+4)
  elif s['phase']==13:
   check('cable fades away at rest',cable.motion_amount<.01 and not cable.audio.is_playing());finish()
 except Exception:finish(traceback.format_exc())
def motion_tick(dt):
 if s['phase']==12:
  m=s['test_mesh'];m.set_world_location(m.get_world_location()+unreal.Vector(0,100*dt,0),False,False)
 tick(dt)
handle=unreal.register_slate_post_tick_callback(motion_tick);ls.editor_request_begin_play()
RESULT={'started':True}
