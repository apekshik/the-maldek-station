"""Exercise actual travel/door interlocks and capture the mixed platform output in PIE."""
import unreal,json,time,traceback
from pathlib import Path
repo=Path(__file__).resolve().parents[4];out=repo/'art/audio/gondola_arrival/runtime';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
s={'phase':'warm','next':time.monotonic()+25,'deadline':time.monotonic()+260,'checks':[],'events':[],'recording':False,'clips':[]}
def check(name,value):
 assert value,name
 if name not in s['checks']:s['checks'].append(name)
def phase(name,delay=0):s.update(phase=name,next=time.monotonic()+delay)
def record(name):
 unreal.AudioMixerLibrary.start_recording_output(w,35);s.update(recording=True,clip=name)
def endrecord():
 if s['recording']:
  unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,s['clip'],str(out));s['clips'].append(s['clip']+'.wav');s['recording']=False

def finish(error=None):
 if 'w' in globals() and w:
  unreal.GameplayStatics.set_global_time_dilation(w,1);endrecord()
 unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(False);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s.update(success=error is None,error=error);(out/'report.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 global w,p,pc,g,sign,mesh,sp,start,end
 if time.monotonic()<s['next']:return
 try:
  assert time.monotonic()<s['deadline'],('Timeout',s['phase'])
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if s['phase']=='warm':
   g=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem)[0];sign=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaStatusSign)[0]
   mesh=next(c for c in g.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh');sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);end=sp.get_location_at_distance_along_spline(sp.get_spline_length(),unreal.SplineCoordinateSpace.WORLD)
   opening=p.get_component_by_class(unreal.StationOpeningComponent)
   if opening:opening.destroy_component(p)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True)
   unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(True)
   check('Startup does not announce or whoosh',not sign.announcement_audio.is_playing() and not g.dock_whoosh_audio.is_playing())
   check('Four native status recordings assigned',len(sign.status_sounds)==4 and all(sign.status_sounds))
   check('Dock recording assigned independently of door audio',g.dock_whoosh_sound is not None and g.dock_whoosh_audio.get_attach_parent()==mesh)
   check('Platform volume and range',sign.announcement_volume==1.5 and sign.announcement_audio.get_editor_property('attenuation_overrides').falloff_distance==4500)
   check('Staged arrival initially away',sign.current_status==unreal.GondolaPlatformStatus.AWAY)
   p.set_actor_location(start+unreal.Vector(0,-470,105),False,True);pc.set_control_rotation(unreal.Rotator(yaw=90));g.wait_time_at_maldek=180
   record('millford_arrival_mix');g.begin_arrival();phase('approach');return
  current=str(sign.current_status)
  if current!=s.get('last_status'):
   if s.get('last_status') is not None:
    check('Status '+current+' plays corresponding recording',sign.announcement_audio.is_playing() and sign.announcement_audio.sound in sign.status_sounds)
    s['events'].append({'status':current,'sound':sign.announcement_audio.sound.get_name(),'route_distance':g.get_route_distance()})
   s['last_status']=current
  state=s['phase']
  if state=='approach':
   if sign.current_status==unreal.GondolaPlatformStatus.ARRIVING:
    check('Arrival bell starts on arriving',sign.announcement_audio.is_playing() and sign.announcement_audio.sound.get_name()=='Platform_Arriving')
    unreal.GameplayStatics.set_global_time_dilation(w,8);phase('near_stop')
  elif state=='near_stop':
   if g.get_route_distance()<160:unreal.GameplayStatics.set_global_time_dilation(w,1);phase('dock')
  elif state=='dock':
   if g.is_docked():
    check('Physical stop whooshes before door opens',g.dock_whoosh_audio.is_playing() and g.door_open_fraction==0 and sign.current_status!=unreal.GondolaPlatformStatus.BOARD)
    phase('board')
  elif state=='board':
   if sign.current_status==unreal.GondolaPlatformStatus.BOARD:
    check('Board chime waits for fully open doors',g.door_open_fraction>=.999 and sign.announcement_audio.sound.get_name()=='Platform_Board')
    phase('hold',3)
  elif state=='hold':
   check('Stable board does not repeat chime or whoosh',not sign.announcement_audio.is_playing() and not g.dock_whoosh_audio.is_playing());endrecord();record('millford_departure_mix');g.send_gondola();phase('depart')
  elif state=='depart':
   if sign.current_status==unreal.GondolaPlatformStatus.DEPART:
    check('Depart warning precedes movement',not g.is_moving() and sign.announcement_audio.sound.get_name()=='Platform_Depart');phase('away')
  elif state=='away':
   if sign.current_status==unreal.GondolaPlatformStatus.AWAY and g.is_moving():
    check('Away cue follows doors closed and movement',g.door_open_fraction==0 and sign.announcement_audio.sound.get_name()=='Platform_Away');phase('transit_setup',2)
  elif state=='transit_setup':
   endrecord();g.cruise_speed=10000;g.approach_speed=1000;g.acceleration=1000;unreal.GameplayStatics.set_global_time_dilation(w,20);p.set_actor_location(end+unreal.Vector(0,-600,105),False,True);phase('far_approach')
  elif state=='far_approach':
   if sp.get_spline_length()-g.get_route_distance()<350:
    unreal.GameplayStatics.set_global_time_dilation(w,1);record('maldek_dock_mix');phase('far_dock')
  elif state=='far_dock':
   if not g.is_moving():
    check('Far terminal also plays docking whoosh',g.dock_whoosh_audio.is_playing());check('Far whoosh uses cabin position', (g.dock_whoosh_audio.get_world_location()-end).length()<300);phase('far_board')
  elif state=='far_board':
   if g.get_platform_status(True)==unreal.GondolaPlatformStatus.BOARD:phase('far_hold',3)
  elif state=='far_hold':
   check('Far dock whoosh does not loop',not g.dock_whoosh_audio.is_playing());endrecord();g.return_gondola();phase('return_start')
  elif state=='return_start':
   if g.is_moving():
    unreal.GameplayStatics.set_global_time_dilation(w,20);p.set_actor_location(start+unreal.Vector(0,-470,105),False,True);phase('return_approach')
  elif state=='return_approach':
   if g.get_route_distance()<500:
    unreal.GameplayStatics.set_global_time_dilation(w,1);record('millford_return_mix');phase('return_dock')
  elif state=='return_dock':
   if g.is_docked():check('Subsequent return also whooshes',g.dock_whoosh_audio.is_playing());phase('return_board')
  elif state=='return_board':
   if sign.current_status==unreal.GondolaPlatformStatus.BOARD:phase('end',3)
  elif state=='end':
   check('Return board settles silently',not sign.announcement_audio.is_playing());finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
