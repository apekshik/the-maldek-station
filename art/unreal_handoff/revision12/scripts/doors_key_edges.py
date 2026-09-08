"""Key-mode interruption and pointer interaction in a second viewport aspect ratio."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+8,'deadline':time.monotonic()+80,'checks':{}};pointer=None
def nextphase(i,wait=.25):s.update(phase=i,next=time.monotonic()+wait)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def point(q):
 global pointer
 pointer=pc.project_world_location_to_screen(d.get_key_grip_world_position(q));unreal.StationMigrationLibrary.send_pie_mouse_position(pointer.x,pointer.y)
def button(down):unreal.StationMigrationLibrary.send_pie_key('LeftMouseButton',down)
def finish(error=None):
 button(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(out/'edges.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc,pointer
 try:
  if pointer:unreal.StationMigrationLibrary.send_pie_mouse_position(pointer.x,pointer.y)
  now=time.monotonic()
  if now<s['next']:return
  assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1024,768);d=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label()=='R12_Door_Control_side');p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,145,102));p.set_actor_location(pos,False,True);pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));nextphase(1,.7);return
  if phase==1:d.try_interact();nextphase(2,.8);return
  if phase==2:check('second_aspect_entry',d.is_using_key());point(0);nextphase(3);return
  if phase==3:button(True);nextphase(4);return
  if phase==4:point(1);nextphase(5,.1);return
  if phase==5:
   check('second_aspect_seated',d.get_key_insertion()>.99);button(False);unreal.StationMigrationLibrary.send_pie_key('RightMouseButton',True);nextphase(6,.1);return
  if phase==6:unreal.StationMigrationLibrary.send_pie_key('RightMouseButton',False);pointer=None;nextphase(7,.5);return
  if phase==7:
   check('cancel_stops_turn_and_fill',not d.get_editor_property('EventAudio').is_playing() and not d.key_inspection_light.is_visible())
   check('cancel_during_turn_keeps_lock',d.is_locked() and not d.is_using_key());check('cancel_restores_both_inputs',not pc.is_move_input_ignored() and not pc.is_look_input_ignored());d.try_interact();nextphase(8,.8);return
  if phase==8:point(0);button(True);nextphase(9);return
  if phase==9:point(.4);nextphase(10);return
  if phase==10:
   check('partial_before_key_removed',d.get_key_insertion()>.3);d.set_editor_property('key_available',False);button(False);pointer=None;nextphase(11,.5);return
  if phase==11:
   check('lost_key_cancels_safely',d.is_locked() and not d.is_using_key() and not pc.is_move_input_ignored());d.set_editor_property('key_available',True);d.try_interact();nextphase(12,.8);return
  if phase==12:check('entry_before_teardown',d.is_using_key());d.destroy_actor();nextphase(13,.5);return
  if phase==13:
   check('teardown_restores_player',pc.get_view_target()==p and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());finish();return
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
