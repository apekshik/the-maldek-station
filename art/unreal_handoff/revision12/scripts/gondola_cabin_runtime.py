"""Actual player-capsule boarding, obstruction, both landings and full rider roundtrip."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_cabin';views=out/'runtime_views';views.mkdir(exist_ok=True)
normal_only=globals().get('JOB',{}).get('normal_departure_only',False)
report_name='normal_runtime.json' if normal_only else 'runtime.json'
if normal_only:views=out/'normal_views';views.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
s={'phase':'warm','next':time.monotonic()+25,'deadline':time.monotonic()+300,'checks':[],'images':[],'recording':False,'busy':False}
def save(): (out/report_name).write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2))
def finish(error=None):
 w=unreal.EditorLevelLibrary.get_game_world()
 if w:
  unreal.GameplayStatics.set_global_time_dilation(w,1)
  if s['recording']:unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'door_capture_partial',str(out))
 unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(False);unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(error=error,passed=error is None);save();unreal.unregister_slate_post_tick_callback(handle)
def phase(name,now):s.update(phase=name,phase_time=now);save()
def shot(name):
 path=views/(name+'.png');assert not s.get('shot_path') or Path(s['shot_path']).exists(),'Prior screenshot not completed';path.unlink(missing_ok=True);unreal.AutomationLibrary.take_high_res_screenshot(1440,900,str(path));s['images'].append(str(path));s['shot_path']=str(path)
def record(w,name):unreal.AudioMixerLibrary.start_recording_output(w,20);s.update(recording=True,record_name=name)
def endrecord(w):unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,s['record_name'],str(out));s['recording']=False
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'],'Cabin runtime check timed out'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);g=next(iter(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem)));mesh=next(c for c in g.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh');now=unreal.GameplayStatics.get_time_seconds(w);q=g.door_open_fraction;local=p.get_actor_location()-mesh.get_world_location();state=str(g.door_phase)
  if g.is_moving():assert q<.0001,('Doors open while moving',q,state)
  def place(x,y,z=105,walk=False):
   p.character_movement.stop_movement_immediately();p.set_actor_location(mesh.get_world_location()+unreal.Vector(x,y,z),False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING if walk else unreal.MovementMode.MOVE_NONE)
  def walkto(y,direction):
   assert now-s['phase_time']<20,('Capsule traversal blocked',s['phase'],local.to_tuple())
   if (direction>0 and local.y<y) or (direction<0 and local.y>y):p.add_movement_input(unreal.Vector(0,direction,0),1,True);return False
   p.character_movement.stop_movement_immediately();return True
  if s['phase']=='warm':
   assert abs(g.get_route_distance()-3048)<1 and q==0
   unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(True);unreal.StationMigrationLibrary.set_pie_render_size(1440,900)
   # Isolate the door recordings in PIE only, for an objectively non-silent capture.
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    if a==g:continue
    if isinstance(a,(unreal.StationCableAudio,unreal.GondolaMechanism)):a.set_actor_tick_enabled(False)
    for c in a.get_components_by_class(unreal.AudioComponent):c.stop();c.set_volume_multiplier(0)
   pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
   start=g.get_components_by_class(unreal.SplineComponent)[0].get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);p.set_actor_location(start+unreal.Vector(0,-470,105),False,True);pc.set_control_rotation(unreal.Rotator(yaw=90));g.wait_time_at_maldek=10;g.begin_arrival();unreal.GameplayStatics.set_global_time_dilation(w,8);phase('arrival',now)
  elif s['phase']=='arrival':
   if g.get_route_distance()<140:
    unreal.GameplayStatics.set_global_time_dilation(w,1);record(w,'opening_in_game');phase('opening',now)
  elif s['phase']=='opening':
   if .35<q<.8 and 'opening_shot' not in s:shot('01_opening');s['opening_shot']=True
   if 'OPEN' in state and 'OPENING' not in state:
    assert g.is_docked();endrecord(w);shot('02_open');s['checks'].append('Arrival stops before opening with recorded audio');place(0,-470,walk=True);phase('board',now)
  elif s['phase']=='board':
   if walkto(-140,1):s['checks'].append('Actual capsule boards Millford through clear opening');unreal.StationMigrationLibrary.send_pie_key('E',True);phase('release',now)
  elif s['phase']=='release':
   unreal.StationMigrationLibrary.send_pie_key('E',False);assert g.is_departure_pending() and not g.is_moving();phase('closing_obstruction',now)
  elif s['phase']=='closing_obstruction':
   if .45<q<.9:place(0,-316);s['obstruction_fraction']=q;phase('reopening',now)
  elif s['phase']=='reopening':
   assert not g.is_moving()
   if q>=.999 and 'OPENING' not in state:phase('hold',now)
  elif s['phase']=='hold':
   assert q>=.999 and not g.is_moving()
   if now-s['phase_time']>2:s['checks'].append('Closing door reverses and holds for obstructing capsule');place(0,-316,walk=True);phase('clear_door',now)
  elif s['phase']=='clear_door':
   if walkto(-140,1):record(w,'closing_in_game');phase('departure',now)
  elif s['phase']=='departure':
   if g.is_moving():
    assert q==0;endrecord(w);s['checks'].append('Recorded closing and latch complete before movement');unreal.GameplayStatics.set_global_time_dilation(w,1 if normal_only else 8);phase('outbound',now)
  elif s['phase']=='outbound':
   assert abs(local.x)<125 and abs(local.y)<260 and 40<local.z<230,('Rider lost outbound',local.to_tuple())
   if normal_only and now-s['phase_time']>=15:
    s['checks'].append('Rider remains on moving floor for 15 seconds at normal game speed');finish();return
   if not g.is_moving():unreal.GameplayStatics.set_global_time_dilation(w,1);phase('far_landing',now)
  elif s['phase']=='far_landing':
   ready=(g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()<1
   if q>0:assert ready,'Door opened before far gangway deployed'
   if q>=.999 and 'OPENING' not in state:
    s['checks'].append('Far gangway deploys before doors open');shot('03_far_open');p.set_actor_location(g.far_boarding_bridge.get_actor_location()+unreal.Vector(0,0,105),False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);phase('far_hold',now)
  elif s['phase']=='far_hold':
   assert not g.is_moving() and q>=.999 and (g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()<1
   if now-s['phase_time']>13:assert g.is_departure_pending();s['checks'].append('Automatic return waits for occupied gangway');phase('far_board',now)
  elif s['phase']=='far_board':
   if walkto(-140,1):s['checks'].append('Actual capsule boards from far gangway');phase('far_depart',now)
  elif s['phase']=='far_depart':
   if q>0:assert (g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()<1
   bridge_travel=(g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()
   if not s.get('late_bridge_test') and q==0 and 30<bridge_travel<150:
    p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);p.set_actor_location(g.far_boarding_bridge.get_actor_location()+unreal.Vector(0,0,105),False,True);s['late_bridge_test']=True;phase('late_bridge_hold',now)
   if g.is_moving():assert q==0 and (g.far_boarding_bridge.get_actor_location()-g.far_bridge_parked).length()<1;s['checks'].append('Far return waits for closed doors and retracted gangway');unreal.GameplayStatics.set_global_time_dilation(w,8);phase('return',now)
  elif s['phase']=='late_bridge_hold':
   assert not g.is_moving()
   if now-s['phase_time']>1:
    # Step back to the fixed landing so the held gangway can finish redeploying.
    place(300,-405);phase('late_bridge_reopen',now)
  elif s['phase']=='late_bridge_reopen':
   assert not g.is_moving()
   if q>0:assert (g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()<1
   if q>=.999 and 'OPENING' not in state:
    s['checks'].append('Late gangway obstruction cancels retraction and redeploys before reopening');place(0,-405,walk=True);phase('far_board',now)
  elif s['phase']=='return':
   assert abs(local.x)<125 and abs(local.y)<260 and 40<local.z<230,('Rider lost return',local.to_tuple())
   if g.is_docked():unreal.GameplayStatics.set_global_time_dilation(w,1);phase('return_open',now)
  elif s['phase']=='return_open':
   if q>=.999 and 'OPENING' not in state:phase('exit',now)
  elif s['phase']=='exit':
   if walkto(-465,-1):s['checks'].append('Actual capsule exits after full roundtrip');shot('04_return_open');phase('finish',now)
  elif s['phase']=='finish':
   if now-s['phase_time']>2:assert all(Path(x).exists() for x in s['images']);finish();return
  s['next']=time.monotonic()+(.001 if s['phase'] in ['board','clear_door','far_board','exit'] else .05)
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
