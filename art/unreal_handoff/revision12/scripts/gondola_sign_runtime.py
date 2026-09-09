"""Real travel/door states, obstruction, boarding, night/neutral sign review."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_sign';views=out/'review';views.mkdir(exist_ok=True)
placement_only=globals().get('JOB',{}).get('placement_only',False)
walk_only=globals().get('JOB',{}).get('walk_only',False)
report_name='approach_walk.json' if walk_only else 'runtime.json'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
light=aa.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(pitch=-40,yaw=-35));light.set_actor_label('Sign_Inspection_Temporary');light.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);light.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
s={'phase':'warm','next':time.monotonic()+25,'deadline':time.monotonic()+420,'checks':[],'images':[],'seen':[],'busy':False}
def save(): (out/report_name).write_text(json.dumps({k:v for k,v in s.items() if k not in ['busy','queue']},indent=2))
def finish(error=None):
 w=unreal.EditorLevelLibrary.get_game_world()
 if w:unreal.GameplayStatics.set_global_time_dilation(w,1)
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(passed=error is None,error=error);save();unreal.unregister_slate_post_tick_callback(handle)
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  aa.destroy_actor(light);unreal.unregister_slate_post_tick_callback(cleanup_handle)
 cleanup_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'],('Timeout',s['phase'])
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);g=next(iter(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem)));a=next(iter(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaStatusSign)))
  carrier=next(c for c in g.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh');now=unreal.GameplayStatics.get_time_seconds(w);q=g.door_open_fraction
  s['player_offset']=(p.get_actor_location()-carrier.get_world_location()).to_tuple()
  start=g.get_components_by_class(unreal.SplineComponent)[0].get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
  lamp=next(x for x in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.DirectionalLight) if x.get_actor_label()=='Sign_Inspection_Temporary').get_component_by_class(unreal.DirectionalLightComponent)
  status=str(g.get_platform_status(False)).split('.')[-1].split(':')[0];far=str(g.get_platform_status(True)).split('.')[-1].split(':')[0]
  if status!=s.get('last_status'):s.update(last_status=status,status_since=time.monotonic());s['seen'].append(status)
  if time.monotonic()-s['status_since']>.3:
   assert a.current_status==g.get_platform_status(False),('Sign lags controller',a.current_status,status)
   values=[c.get_material(0).get_scalar_parameter_value('GlowStrength') for c in a.circuits]
   wanted=['BOARD','ARRIVING','DEPART','AWAY'].index(status)
   assert all(abs(v-(a.lit_strength if i==wanted else a.unlit_strength))<.001 for i,v in enumerate(values)),values
  if 'sign_position' in s:assert (a.get_actor_location()-unreal.Vector(*s['sign_position'])).length()<.01,'Sign moved with cabin'
  if g.is_moving():assert q==0 and status!='BOARD'
  def phase(name):s.update(phase=name,phase_time=now);save()
  def place(x,y,z=105,walk=False):
   p.character_movement.stop_movement_immediately();p.set_actor_location(carrier.get_world_location()+unreal.Vector(x,y,z),False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING if walk else unreal.MovementMode.MOVE_NONE)
  def shotqueue(entries,after):
   g.set_actor_tick_enabled(False);unreal.GameplayStatics.set_global_time_dilation(w,1);s.update(queue=list(entries),after=after);phase('view_place')
  if s['phase']=='warm':
   assert status=='AWAY';s['sign_position']=a.get_actor_location().to_tuple();s['checks'].append('Initially away; sign is independent of cabin')
   pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);unreal.StationMigrationLibrary.set_pie_render_size(1440,900)
   g.wait_time_at_maldek=180
   if walk_only:g.begin_arrival();unreal.GameplayStatics.set_global_time_dilation(w,8);phase('arrive')
   else:shotqueue([('01_away_night','front',0,False)],'begin_arrival')
  elif s['phase']=='view_place':
   name,view,lux,torch=s['queue'][0];origin=a.get_actor_location()
   if view=='approach':eye=start+unreal.Vector(0,-740,180);target=start+unreal.Vector(100,-330,190)
   elif view=='rear':eye=origin+unreal.Vector(-150,300,235);target=origin+unreal.Vector(0,20,203)
   else:eye=origin+unreal.Vector(-80 if view=='front' else -140,-180,240);target=origin+unreal.Vector(0,0,218)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,target));lamp.set_intensity(lux)
   torchcomp=p.get_components_by_class(unreal.SpotLightComponent)[0]
   if torchcomp.is_visible()!=torch:p.toggle_flashlight()
   s.update(phase='capture',next=time.monotonic()+3)
  elif s['phase']=='capture':
   name=s['queue'][0][0];path=views/(name+'.png');path.unlink(missing_ok=True);unreal.AutomationLibrary.take_high_res_screenshot(1440,900,str(path));s['images'].append(str(path));s.update(phase='image_wait',next=time.monotonic()+.2)
  elif s['phase']=='image_wait':
   if not Path(s['images'][-1]).exists():return
   s['queue'].pop(0)
   if s['queue']:phase('view_place')
   else:
    lamp.set_intensity(0);g.set_actor_tick_enabled(True);phase(s['after'])
  elif s['phase']=='begin_arrival':
   place(0,-480);g.begin_arrival();unreal.GameplayStatics.set_global_time_dilation(w,8);phase('arrive')
  elif s['phase']=='arrive':
   if status=='ARRIVING' and not s.get('arrival_shot') and not walk_only:
    s['arrival_shot']=True;shotqueue([('02_arriving_night','front',0,False)],'resume_arrive')
   elif status=='BOARD':
    assert not g.is_moving() and q==1;s['checks'].append('ARRIVING through approach and opening; BOARD only fully open')
    if walk_only:unreal.GameplayStatics.set_global_time_dilation(w,1);phase('start_board')
    else:shotqueue([('03_board_night','front',0,False),('04_board_torch','front',0,True),('05_board_neutral','front',3,False),('06_board_glancing','glance',3,False),('07_placement_left','approach',3,False),('08_rear','rear',3,False)],'start_board')
  elif s['phase']=='resume_arrive':place(0,-480);unreal.GameplayStatics.set_global_time_dilation(w,8);phase('arrive')
  elif s['phase']=='start_board':place(0,-740,walk=True);phase('board')
  elif s['phase']=='board':
   assert now-s['phase_time']<20,'Boarding path blocked'
   if (p.get_actor_location()-carrier.get_world_location()).y<-140:p.add_movement_input(unreal.Vector(0,1,0),1,True)
   else:
    p.character_movement.stop_movement_immediately();s['checks'].append('Actual player capsule boards with sign installed')
    if placement_only and not s.get('walked_exit'):phase('walk_exit')
    elif walk_only:s['checks'].append('Normal-speed approach, boarding, exit and reboarding past final sign');finish();return
    else:unreal.StationMigrationLibrary.send_pie_key('E',True);phase('release')
  elif s['phase']=='walk_exit':
   assert now-s['phase_time']<20,('Exit path blocked',s['player_offset'])
   if (p.get_actor_location()-carrier.get_world_location()).y>-740:p.add_movement_input(unreal.Vector(0,-1,0),1,True)
   else:s['walked_exit']=True;s['checks'].append('Capsule exits unobstructed at final left placement');phase('start_board')
  elif s['phase']=='release':unreal.StationMigrationLibrary.send_pie_key('E',False);assert g.is_departure_pending();phase('obstruct')
  elif s['phase']=='obstruct':
   if .4<q<.9:place(0,-316);phase('reopen')
  elif s['phase']=='reopen':
   assert not g.is_moving() and status=='DEPART'
   if q==1:s['checks'].append('DEPART remains lit while obstructed doors reopen');shotqueue([('09_depart_hold','front',0,False)],'clear')
  elif s['phase']=='clear':place(0,-140);phase('depart')
  elif s['phase']=='depart':
   if g.is_moving():assert q==0;s['checks'].append('AWAY after latched departure');unreal.GameplayStatics.set_global_time_dilation(w,8);phase('outbound')
  elif s['phase']=='outbound':
   assert status=='AWAY'
   if placement_only and g.get_route_distance()>600:
    s['checks'].append('Final placement remains fixed after departure');assert set(s['seen'])=={'BOARD','ARRIVING','DEPART','AWAY'};finish();return
   if far=='BOARD':assert not g.is_moving() and q==1;s['checks'].append('Far terminal BOARD waits for deployed gangway and open doors');g.return_gondola();phase('far_depart')
  elif s['phase']=='far_depart':
   assert status=='AWAY'
   if g.is_moving():assert q==0;phase('return')
  elif s['phase']=='return':
   if status=='ARRIVING':s['checks'].append('ARRIVING switches on within the return approach zone');phase('home')
  elif s['phase']=='home':
   if status=='BOARD':
    unreal.GameplayStatics.set_global_time_dilation(w,1);place(0,-140,walk=True);phase('exit')
  elif s['phase']=='exit':
   assert now-s['phase_time']<20,'Exit blocked'
   if (p.get_actor_location()-carrier.get_world_location()).y>-480:p.add_movement_input(unreal.Vector(0,-1,0),1,True)
   else:
    s['checks'].append('Actual capsule exits after full roundtrip; sign stayed fixed');assert set(s['seen'])=={'BOARD','ARRIVING','DEPART','AWAY'};finish();return
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
