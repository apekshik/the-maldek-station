import unreal,json,time,traceback,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';(out/'views').mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
info=json.loads((out/'installation.json').read_text());centre=unreal.Vector(*info['centre_world']);forward=unreal.Vector(*info['forward'])
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
tests=[('retreat',[-160,-20,-160],False,160,60),('walk_through',[-180,180],True,180,60),('return_through',[180,-180],True,180,60),('sprint_30fps',[-220,220],True,500,30)]
s={'phase':'warm','next':time.monotonic()+15,'deadline':time.monotonic()+220,'index':0,'results':[],'samples':[],'busy':False}
def save(): (out/'playtest.json').write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2))
def end(error=None):
 if error:s['error']=error
 if s.get('recording'):
  unreal.AudioMixerLibrary.stop_recording_output(unreal.EditorLevelLibrary.get_game_world(),unreal.AudioRecordingExportType.WAV_FILE,'tape_crossing_mix',str(out));s['recording']=False
 s['passed']=not error and len(s['results'])==4 and all(r['passed'] for r in s['results']);s['phase']='finished';save()
 if 'original_speed' in globals() and isinstance(pawn,unreal.Character):pawn.character_movement.max_walk_speed=original_speed
 unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(False)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 unreal.SystemLibrary.execute_console_command(None,'t.MaxFPS 0');unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 global pawn,original_speed
 if s['busy']:return
 s['busy']=True
 try:
  now=time.monotonic();assert now<s['deadline'],'test deadline'
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
  if not pawn:return
  tape=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StationPoliceTape) if a.crossing)
  if now<s['next']:return
  if s['phase']=='warm':
   original_speed=pawn.character_movement.max_walk_speed;s['audio_capture_override']=dict(unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(True));unreal.AudioMixerLibrary.start_recording_output(world,90);s['recording']=True;unreal.StationMigrationLibrary.set_pie_render_size(1440,810);s['phase']='place'
  if s['phase']=='place':
   name,points,expected,speed,fps=tests[s['index']]
   if name!='return_through':tape.reset_tape()
   pawn.character_movement.stop_movement_immediately();pawn.character_movement.max_walk_speed=speed
   location=centre+forward*points[0];location.z=info['ground_world_z']+pawn.capsule_component.get_scaled_capsule_half_height()+8
   pawn.set_actor_location(location,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(location+unreal.Vector(0,0,64),centre+unreal.Vector(0,0,125)))
   unreal.SystemLibrary.execute_console_command(world,f't.MaxFPS {fps}')
   s.update(phase='settle',next=now+3,point=1,started=now,samples=[],initial_broken=tape.broken_strands,initial_audio=tape.tear_sound_events);return
  name,points,expected,speed,fps=tests[s['index']]
  if s['phase']=='settle':
   if s['index']==0:unreal.AutomationLibrary.take_high_res_screenshot(1440,810,str(out/'views/intact.png'))
   s.update(phase='walk',started=now)
  if s['phase']=='walk':
   loc=pawn.get_actor_location();target=centre+forward*points[s['point']];delta=target-loc;delta.z=0;distance=delta.length()
   s['samples'].append({'elapsed':now-s['started'],'distance':distance,'broken':tape.broken_strands,'contact':tape.contact_seconds,'ribbon_contacts':tape.ribbon_contacts,'location':[loc.x,loc.y,loc.z]})
   if distance<9:
    pawn.character_movement.stop_movement_immediately();s['point']+=1
    if s['point']==len(points):
     passed=(tape.broken_strands==3 if expected else tape.broken_strands==0)
     events=tape.tear_sound_events-s['initial_audio'];audio_ok=(events==0 if name in ['retreat','return_through'] else 1<=events<=3);passed=passed and audio_ok
     s['results'].append({'name':name,'passed':passed,'new_tear_sound_events':events,'audio_passed':audio_ok,'broken':tape.broken_strands,'initial_broken':s['initial_broken'],'fps_cap':fps,'speed':speed,'duration':now-s['started'],'max_contact':tape.contact_seconds,'ribbon_contacts':tape.ribbon_contacts});save()
     if name=='walk_through':pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(loc,centre+unreal.Vector(0,0,90)));unreal.AutomationLibrary.take_high_res_screenshot(1440,810,str(out/'views/torn.png'))
     s['index']+=1
     if s['index']==len(tests):end();return
     s.update(phase='place',next=now+2);return
   else:pawn.add_movement_input(delta/distance,min(1.,max(.15,distance/80)),True)
   assert now-s['started']<18,'route did not finish'
 except Exception:end(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
