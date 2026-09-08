"""Actual PIE arrival, full outbound, wait and return; acceleration uses game time."""
import unreal,json,time,traceback,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';views=out/'views';views.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
s={'phase':'warmup','next':time.monotonic()+15,'deadline':time.monotonic()+280,'busy':False,'samples':[],'max_relative_error_cm':0,'images':[]}
def v(p):return [p.x,p.y,p.z]
def finish():
 w=unreal.EditorLevelLibrary.get_game_world()
 if w:unreal.GameplayStatics.set_global_time_dilation(w,1)
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 (out/'runtime.json').write_text(json.dumps({k:z for k,z in s.items() if k not in ['g','parts','offsets']},indent=2));unreal.unregister_slate_post_tick_callback(handle)
def shot(name):
 path=views/(name+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1440,900,str(path));s['images'].append(str(path))
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'],'Runtime validation timed out'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);g=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem));mesh=g.get_components_by_class(unreal.StaticMeshComponent)[0]
  distance=g.get_route_distance();now=unreal.GameplayStatics.get_time_seconds(w)
  if s['phase']=='warmup':
   s['initial_distance_cm']=distance;assert abs(distance-3048)<1 and not g.is_moving() and not g.is_docked()
   s['parts']=list(g.cabin_parts);s['offsets']=[a.get_actor_location()-mesh.get_world_location() for a in s['parts']];s['assembly_parts']=len(s['parts'])
   unreal.StationMigrationLibrary.set_pie_render_size(1440,900);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);p.character_movement.stop_movement_immediately();p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
   start=g.get_components_by_class(unreal.SplineComponent)[0].get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
   eye=start+unreal.Vector(0,-480,165);p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,start+unreal.Vector(0,3048,170)))
   s.update(phase='arrival',arrival_start=now,next=time.monotonic()+.5)
  else:
   for a,offset in zip(s['parts'],s['offsets']):
    err=((a.get_actor_location()-mesh.get_world_location())-offset).length();s['max_relative_error_cm']=max(s['max_relative_error_cm'],err)
   assert abs(mesh.get_world_rotation().pitch)<.01 and abs(mesh.get_world_rotation().roll)<.01
   if s['phase']=='arrival':
    if 'arrival_shot' not in s and now-s['arrival_start']>2:shot('01_first_arrival');s['arrival_shot']=True
    if g.is_docked():
     s['arrival_seconds']=now-s['arrival_start'];assert 36<s['arrival_seconds']<48;shot('02_docked');s.update(phase='depart',next=time.monotonic()+3)
   elif s['phase']=='depart':
    p.set_actor_location(mesh.get_world_location()+unreal.Vector(0,-480,105),False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);pc.set_ignore_move_input(False);s.update(phase='boardwalk',board_start=now)
   elif s['phase']=='boardwalk':
    local=p.get_actor_location()-mesh.get_world_location()
    assert now-s['board_start']<25,('Boarding blocked',v(local))
    if local.y < -150:p.add_movement_input(unreal.Vector(0,1,0),1,True)
    else:
     p.character_movement.stop_movement_immediately();pc.set_ignore_move_input(True);s['boarded_position']=v(local);shot('03_boarded');s.update(phase='press_depart',next=time.monotonic()+2)
   elif s['phase']=='press_depart':
    unreal.StationMigrationLibrary.send_pie_key('E',True);s.update(phase='release_depart',next=time.monotonic()+.1)
   elif s['phase']=='release_depart':
    unreal.StationMigrationLibrary.send_pie_key('E',False);assert g.is_moving(),'E did not start the trip';s.update(phase='outbound',depart_time=now);unreal.GameplayStatics.set_global_time_dilation(w,8)
   elif s['phase']=='outbound':
    relative=p.get_actor_location()-mesh.get_world_location();assert abs(relative.x)<125 and abs(relative.y)<260 and 40<relative.z<230,('Rider left cabin',v(relative));s['rider_position']=v(relative)
    s['samples'].append({'time':now-s['depart_time'],'distance_cm':distance,'position':v(mesh.get_world_location())})
    if not g.is_moving():
     s['outbound_seconds']=now-s['depart_time'];s['far_distance_cm']=distance;s['far_rider_position']=v(p.get_actor_location()-mesh.get_world_location());assert 360<s['outbound_seconds']<480;assert not g.is_docked();s.update(phase='wait',far_arrival=now)
   elif s['phase']=='wait':
    if now-s['far_arrival']>172:
     bridge=g.far_boarding_bridge;assert (bridge.get_actor_location()-g.far_bridge_deployed).length()<1
     p.set_actor_location(bridge.get_actor_location()+unreal.Vector(0,0,100),False,True);s.update(phase='bridge_hold',hold_start=now)
   elif s['phase']=='bridge_hold':
    assert not g.is_moving() and (g.far_boarding_bridge.get_actor_location()-g.far_bridge_deployed).length()<1
    if now-s['hold_start']>14:
     s['occupied_bridge_held']=True;pc.set_ignore_move_input(False);s.update(phase='bridge_walk',walk_start=now)
   elif s['phase']=='bridge_walk':
    local=p.get_actor_location()-mesh.get_world_location();assert now-s['walk_start']<25,('Far boarding blocked',v(local))
    if local.y < -150:p.add_movement_input(unreal.Vector(0,1,0),1,True)
    else:
     p.character_movement.stop_movement_immediately();pc.set_ignore_move_input(True);s.update(phase='wait_return')
   elif s['phase']=='wait_return':
    if g.is_moving():s.update(phase='return',return_start=now,wait_seconds=now-s['far_arrival']);assert (g.far_boarding_bridge.get_actor_location()-g.far_bridge_parked).length()<1
   elif s['phase']=='return':
    relative=p.get_actor_location()-mesh.get_world_location();assert abs(relative.x)<125 and abs(relative.y)<260 and 40<relative.z<230,('Rider left cabin on return',v(relative))
    if g.is_docked():
     s['return_seconds']=now-s['return_start'];assert 350<s['return_seconds']<480;assert distance<.5;assert s['max_relative_error_cm']<1
     s['passed']=True;finish();return
   s['next']=max(s['next'],time.monotonic()+(.001 if s['phase'] in ['boardwalk','bridge_walk'] else .15))
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
