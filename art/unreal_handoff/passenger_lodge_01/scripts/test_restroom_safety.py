"""PIE-only blocked-swing and legacy mechanical/keypad regression."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
s={'phase':0,'index':0,'next':time.monotonic()+12,'deadline':time.monotonic()+180,'checks':{}}
def advance(n,wait=.3):s.update(phase=n,next=time.monotonic()+wait)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def put(a,x,y):
 p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.MathLibrary.transform_location(a.get_actor_transform(),unreal.Vector(x,y,99/a.get_actor_scale3d().z)),False,True)
 pc.set_control_rotation(unreal.Rotator(yaw=a.get_actor_rotation().yaw+(-90 if y>0 else 90)))
def finish(error=None):
 unreal.StationMigrationLibrary.send_pie_key('E',False);s.update(success=error is None,error=error);(OUT/'restrooms/safety.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global p,pc,doors,d,label
 if time.monotonic()<s['next']:return
 try:
  assert time.monotonic()<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)}
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   advance(1);return
  if phase==1:
   if s['index']==5:advance(10);return
   label=['MIG_PLR_Women_Entry','MIG_PLR_Men_Entry','MIG_PLR_Women_A','MIG_PLR_Women_B','MIG_PLR_Men_A'][s['index']];d=doors[label];put(d,-55 if 'Entry' in label else 55,55 if 'Entry' in label else -55);d.unlock();d.try_interact();advance(2,2);return
  if phase==2:
   angle=abs(d.get_open_angle());check(label+'_blocked_before_full_swing',.1<angle<80);s.setdefault('blocked_angles',{})[label]=angle;put(d,-45 if 'Entry' in label else 39,-140 if 'Entry' in label else 80);d.try_interact();advance(3,2);return
  if phase==3:check(label+'_safe_close',abs(d.get_open_angle())<.01 and not d.is_locked());d.unlock();d.try_interact();advance(4,2);return
  if phase==4:check(label+'_clear_reopen',abs(d.get_open_angle()-d.open_angle)<.1);d.try_interact();advance(5,2);return
  if phase==5:check(label+'_final_closed',abs(d.get_open_angle())<.01 and not d.is_locked());s['index']+=1;advance(1);return
  if phase==10:
   d=doors['R12_Door_Control_side'];check('legacy_opt_out',not d.use_authored_hardware and abs(d.key_face_depth-4.6)<.001 and d.interior_is_negative_y);put(d,65,150);d.lock();advance(10.5,.7);return
  if phase==10.5:d.try_interact();advance(11,.8);return
  if phase==11:check('legacy_key_camera',d.is_using_key() and pc.get_view_target()==d);unreal.StationMigrationLibrary.send_pie_key('E',True);advance(12,.15);return
  if phase==12:unreal.StationMigrationLibrary.send_pie_key('E',False);advance(13,.7);return
  if phase==13:check('legacy_cancel',not d.is_using_key() and d.is_locked() and pc.get_view_target()==p);d.unlock();d.try_interact();advance(14,2);return
  if phase==14:check('legacy_swing',abs(d.get_open_angle()-d.open_angle)<.1);d.try_interact();advance(15,2);return
  if phase==15:
   check('legacy_relock',d.is_locked() and abs(d.get_open_angle())<.01);d=doors['R12_Door_Control_front'];check('keypad_opt_out',d.has_keypad and not d.use_authored_hardware);put(d,50,150);d.lock();check('bad_code_rejected',not d.submit_code('0000') and d.is_locked());check('1234_accepted',d.submit_code('1234') and not d.is_locked());advance(16,2);return
  if phase==16:check('keypad_input_restored',not pc.is_move_input_ignored() and not pc.is_look_input_ignored());finish();return
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
