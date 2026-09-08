"""Check input limits, obstruction/re-lock timing, and inward standard-door audio in PIE."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'recorded_audio'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+9,'deadline':time.monotonic()+100,'checks':{}}
def check(n,v):s['checks'][n]=bool(v);assert v,n
def key(k):unreal.StationMigrationLibrary.send_pie_key(k,True);unreal.StationMigrationLibrary.send_pie_key(k,False)
def place(y):
 p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,y,105/d.get_actor_scale3d().z)),False,True)
 p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90))
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(success=error is None,error=error)
 (out/'edges.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global p,pc,d,q
 now=time.monotonic()
 if now<s['next']:return
 try:
  assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  if s['phase']==0:
   p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
   if not p:return
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)}
   d=doors['R12_Door_Control_front'];q=doors['R12_Door_Quarters'];place(190)
   check('empty_code_rejected',not d.submit_code(''));check('empty_code_has_feedback',d.get_editor_property('KeypadAudio').sound==d.reject_sound)
   s.update(phase=1,next=now+1);return
  if s['phase']==1:key('E');s.update(phase=2,next=now+.8,count=0);return
  if s['phase']==2:
   key('One');s['count']+=1;s['next']=now+.16
   if s['count']==9:s.update(phase=3,next=now+.2)
   return
  if s['phase']==3:
   check('entry_limit_feedback',d.get_editor_property('KeypadAudio').sound==d.reject_sound)
   check('entry_limit_stays_locked',d.is_locked());d.cancel_keypad_interaction()
   check('valid_code_unlocks',d.submit_code('1234'));place(190);d.try_interact();s.update(phase=4,next=now+3);return
  if s['phase']==4:
   check('open_before_obstruction',d.get_open_angle()>94);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   place(35);d.try_interact();s.update(phase=5,next=now+2);return
  if s['phase']==5:
   s['obstructed_angle']=d.get_open_angle();check('blocked_before_shut',d.get_open_angle()>.1)
   check('blocked_stays_unlocked',not d.is_locked());check('blocked_motion_stops',not d.get_editor_property('MotionAudio').is_playing())
   check('no_false_closing_impact',d.get_editor_property('EventAudio').sound!=d.close_sound)
   check('cannot_lock_obstructed',not d.lock());place(190);d.try_interact();s.update(phase=6,next=now+3);return
  if s['phase']==6:
   check('clear_door_shuts_and_locks',abs(d.get_open_angle())<.01 and d.is_locked())
   check('bolt_engaged_after_shut',d.get_editor_property('LockAudio').sound==d.lock_sound)
   check('standard_starts_unlocked',not q.is_locked());q.try_interact();s.update(phase=7,next=now+3);return
  if s['phase']==7:
   check('inward_door_opens',q.get_open_angle()<-94);q.try_interact();s.update(phase=8,next=now+3);return
  if s['phase']==8:
   check('standard_shuts_without_locking',abs(q.get_open_angle())<.01 and not q.is_locked())
   check('standard_impact',q.get_editor_property('EventAudio').sound==q.close_sound)
   check('standard_motion_stops',not q.get_editor_property('MotionAudio').is_playing());finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
