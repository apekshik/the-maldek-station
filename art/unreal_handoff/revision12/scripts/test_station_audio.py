"""PIE approach boundary, one-shot transition, loop persistence and restart checks."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'station_audio';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'checks':[],'deadline':time.monotonic()+120}
def check(name,condition):
 assert condition,name
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
  c=p.get_component_by_class(unreal.StationOpeningComponent)
  if c.elapsed<7:return
  def place(distance):
   p.character_movement.stop_movement_immediately()
   q=c.station_approach_location+unreal.Vector(0,-distance,100)
   p.set_actor_location(q,False,True)
  if s['phase']==0:
   check('A raised about 10dB',abs(c.atmosphere_volume-1.75)<.01)
   check('B raised about 10dB',abs(c.station_atmosphere_volume-1.4)<.01)
   check('B has 60 second hold',abs(c.station_atmosphere_hold_seconds-60)<.01)
   c.set_editor_property('station_atmosphere_hold_seconds',8.) # shorten only this PIE instance
   check('A opening asset assigned',c.opening_atmosphere.get_name()=='Opening_Atmosphere')
   check('A has 35 second duration',abs(c.opening_atmosphere.duration-35)<.1)
   check('B assigned with creator loop',c.station_atmosphere.get_name()=='Station_Atmosphere' and c.station_atmosphere.get_editor_property('looping'))
   check('Parking does not trigger B',c.station_atmosphere_start_count==0 and not c.is_station_atmosphere_playing())
   unreal.AudioMixerLibrary.start_recording_output(w,25)
   place(c.station_approach_radius+200);s.update(phase=1,next=c.elapsed+1)
  elif c.elapsed<s['next']:return
  elif s['phase']==1:
   check('Outside approach remains silent',c.station_atmosphere_start_count==0)
   place(c.station_approach_radius-300);s.update(phase=2,next=c.elapsed+1)
  elif s['phase']==2:
   check('Approach starts B exactly once',c.station_atmosphere_start_count==1 and c.is_station_atmosphere_playing())
   s.update(phase=3,next=c.elapsed+6)
  elif s['phase']==3:
   check('B survives fade-in',c.is_station_atmosphere_playing())
   place(c.station_approach_radius+200);s.update(phase=4,next=c.elapsed+1)
  elif s['phase']==4:
   check('Leaving does not abruptly stop B',c.is_station_atmosphere_playing())
   place(c.station_approach_radius-300);s.update(phase=5,next=c.elapsed+1)
  elif s['phase']==5:
   check('Reentry does not restart or stack B',c.station_atmosphere_start_count==1)
   pc=unreal.GameplayStatics.get_player_controller(w,0)
   check('Opening input released',not pc.is_move_input_ignored() and not pc.is_look_input_ignored())
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'approach_mix',str(out))
   s.update(phase=6,next=c.elapsed+13)
  elif s['phase']==6:
   check('B eventually fades to silence',not c.is_station_atmosphere_playing())
   check('B does not retrigger after fade',c.station_atmosphere_start_count==1)
   finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play()
RESULT={'started':True}
