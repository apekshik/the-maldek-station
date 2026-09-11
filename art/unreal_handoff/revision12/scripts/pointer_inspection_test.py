"""Real PIE input and lifecycle regression checks. Does not save or modify the station map."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'pointer_inspection_test'
out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor(),'End the current play session before running the test'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground')
settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
state={'checks':{},'busy':False,'next':time.monotonic()+12,'deadline':time.monotonic()+240}
def check(name,value):
 state['checks'][name]=bool(value)
 assert value,name
def key(name,down=None):
 if down is None:
  unreal.StationMigrationLibrary.send_pie_key(name,True)
  unreal.StationMigrationLibrary.send_pie_key(name,False)
 else:unreal.StationMigrationLibrary.send_pie_key(name,down)
def dist(a,b):return (a-b).length()
def same_rotation(a,b):return abs(a.x*b.x+a.y*b.y+a.z*b.z+a.w*b.w)>.99999
def same_pose(a,b,tol=.01):return dist(a.translation,b.translation)<tol and dist(a.scale3d,b.scale3d)<tol and same_rotation(a.rotation,b.rotation)
def run():
 w=unreal.EditorLevelLibrary.get_game_world()
 p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
 check('horror_controller_component',pc and pc.object_inspection)
 comp=pc.object_inspection
 # Cancel the opening through its existing development shortcut, then use the saved parking checkpoint.
 unreal.SystemLibrary.execute_console_command(w,'StationDoorCheckpoint',pc);yield 1
 marker=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.TargetPoint) if a.actor_has_tag('InspectionTestCheckpoint'))
 p.set_actor_location(marker.get_actor_location(),False,True);pc.set_control_rotation(marker.get_actor_rotation())
 p.character_movement.stop_movement_immediately();yield 1
 objects=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationInspectable)
 demo=[o for o in objects if o.actor_has_tag('ParkingInspectionCassette')]
 check('saved_parking_cassette_exists',len(demo)==1)
 obj=demo[0]
 def aim():
  # Aim using the actual animated camera, allowing its view offset to settle.
  for attempt in range(30):
   cam=unreal.GameplayStatics.get_player_camera_manager(w,0)
   desired=unreal.MathLibrary.find_look_at_rotation(cam.get_camera_location(),obj.get_actor_location())
   actual=cam.get_camera_rotation();control=pc.get_control_rotation()
   pc.set_control_rotation(unreal.Rotator(pitch=control.pitch+desired.pitch-actual.pitch,yaw=control.yaw+desired.yaw-actual.yaw,roll=control.roll))
   yield .15
   if comp.has_focused_object():break
 yield from aim()

 original=obj.get_actor_transform();collision=obj.mesh.get_collision_enabled()
 presentation=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
 focus=presentation.get_target_focus()
 # Occluders must block the forgiving targeting query.
 cam=unreal.GameplayStatics.get_player_camera_manager(w,0)
 control=pc.get_control_rotation()
 unreal.SystemLibrary.execute_console_command(w,'StationInspectionDemo',pc)
 blocker=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationInspectable) if a.actor_has_tag('InspectionDemo'))
 blocker.set_editor_property('can_inspect',False)
 blocker.set_actor_location(cam.get_camera_location()+unreal.MathLibrary.get_forward_vector(cam.get_camera_rotation())*60,False,True)
 pc.set_control_rotation(control)
 blocker.mesh.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
 blocker.mesh.set_collision_profile_name('BlockAll');blocker.set_actor_scale3d(unreal.Vector(.3,.3,.3));yield .3
 check('wall_blocks_pickup',not comp.has_focused_object());blocker.destroy_actor();yield .3
 yield from aim()
 check('focus_detected',comp.has_focused_object())
 key('LeftMouseButton');yield .8
 check('click_enters_inspection',comp.phase==unreal.StationInspectionPhase.INSPECTING)
 check('move_and_look_locked',pc.is_move_input_ignored() and pc.is_look_input_ignored())
 check('physical_object_lifted',dist(obj.get_actor_location(),original.translation)>20)
 check('held_collision_disabled',obj.mesh.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION)
 home=obj.get_actor_transform()
 unreal.StationMigrationLibrary.send_pie_mouse_position(400,300)
 key('LeftMouseButton',True)
 unreal.StationMigrationLibrary.send_pie_mouse_position(600,350)
 key('LeftMouseButton',False)
 yield .5
 check('drag_between_ticks_rotates',not same_rotation(obj.get_actor_transform().rotation,home.rotation))
 key('R');yield .6
 key('Right',True);yield .8
 state['rotation_diagnostics']={'phase':str(comp.phase),'before':home.rotation.to_tuple(),'after':obj.get_actor_transform().rotation.to_tuple()}
 key('Right',False);yield .4
 check('raw_rotation_input',not same_rotation(obj.get_actor_transform().rotation,home.rotation))
 key('MouseScrollUp');yield .4
 check('raw_scroll_zooms',dist(obj.get_actor_location(),home.translation)>.2)
 check('scroll_does_not_change_flashlight',abs(focus-presentation.get_target_focus())<.0001)
 comp.zoom_object(10000);yield .5
 near=obj.get_actor_location();comp.zoom_object(10000);yield .6
 check('near_zoom_clamped',dist(near,obj.get_actor_location())<.1)
 comp.zoom_object(-10000);yield .6
 far=obj.get_actor_location();comp.zoom_object(-10000);yield .6
 check('far_zoom_clamped',dist(far,obj.get_actor_location())<.1)
 key('R');yield .8
 check('R_restores_pose',same_pose(obj.get_actor_transform(),home,.05))
 comp.rotate_object(600,0);yield .8
 key('E');yield .8
 check('E_returns_to_idle',not comp.is_inspecting_object())
 check('original_transform_restored',same_pose(obj.get_actor_transform(),original,.001))
 check('collision_restored',obj.mesh.get_collision_enabled()==collision)
 check('input_and_camera_restored',not pc.is_move_input_ignored() and not pc.is_look_input_ignored() and pc.get_view_target()==p)
 # Repeated inspect/return must not drift or accumulate input-lock counts.
 for i in range(3):
  yield from aim()
  key('E');yield .7
  check('repeat_pickup_'+str(i),comp.is_inspecting_object())
  key('Tab');yield .7
  check('repeat_return_'+str(i),not comp.is_inspecting_object() and same_pose(obj.get_actor_transform(),original,.001))
 # Abort during pickup, including an additional external lock that must survive cleanup.
 yield from aim()
 key('E');yield .04
 pc.set_ignore_move_input(True);comp.cancel_inspection();yield .1
 check('external_lock_preserved',pc.is_move_input_ignored())
 pc.set_ignore_move_input(False)
 check('pickup_cancel_restores',not comp.is_inspecting_object() and same_pose(obj.get_actor_transform(),original,.001))
 yield .2
 yield from aim()
 key('E');yield .7
 obj.destroy_actor();yield .3
 check('destroyed_prop_releases_player',not comp.is_inspecting_object() and not pc.is_move_input_ignored() and not pc.is_look_input_ignored())
 unreal.SystemLibrary.execute_console_command(w,'StationInspectionDemo',pc);yield .8
 key('E');yield .7
 unreal.SystemLibrary.execute_console_command(w,'StationDoorCheckpoint',pc);yield .5
 check('teleport_cancels_inspection',not comp.is_inspecting_object() and pc.get_view_target()==p and not pc.is_look_input_ignored())
 # The normal door/keypad path must still be usable after inspection cleanup.
 check('door_system_still_present',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor))>=4)
 state['success']=True

sequence=run()
def finish(error=None):
 for name in ['E','Right','LeftMouseButton','Z','X']:key(name,False)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 state['success']=error is None;state['error']=error;state['busy']=False
 (out/'runtime_report.json').write_text(json.dumps(state,indent=2))
 unreal.unregister_slate_post_tick_callback(handle)
 ls.editor_request_end_play()
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  assert time.monotonic()<state['deadline'],'Test timeout'
  state['next']=time.monotonic()+next(sequence)
 except StopIteration:finish()
 except Exception:finish(traceback.format_exc())
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
ls.editor_request_begin_play()
RESULT={'started':True}
