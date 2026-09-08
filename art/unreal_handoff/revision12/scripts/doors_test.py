"""Actual PIE interaction, collision, code gate, and obstruction checks; no saved test actors."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+8,'deadline':time.monotonic()+120,'checks':{}}
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
control_editor=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='R12_Door_Control_front')
test_actor=aa.spawn_actor_from_class(unreal.load_class(None,'/Game/MaldekRefinement/R12/Doors/BP_StationDoor_Keypad.BP_StationDoor_Keypad_C'),control_editor.get_actor_location()+unreal.Vector(0,0,2500))
test_actor.set_actor_label('D03_Transient_Keypad_Test');test_actor.set_editor_property('access_code','0426')
def key(k):
 unreal.StationMigrationLibrary.send_pie_key(k,True);unreal.StationMigrationLibrary.send_pie_key(k,False)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s['success']=error is None;s['error']=error
 (out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  s['temporary_test_actor_removed']=aa.destroy_actor(test_actor);(out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(clean_handle)
 clean_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 global front,secure,p,pc,w
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   doors=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label()!='D03_Transient_Keypad_Test'];check('two_standard_control_doors',len(doors)==2 and all(not a.is_locked() for a in doors))
   front=next(a for a in doors if abs(a.get_actor_rotation().yaw)<1)
   p.set_actor_location(front.get_actor_location()+unreal.Vector(65,190,98),False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=-90,pitch=0))
   s.update(phase=1,next=now+1);return
  if s['phase']==1:
   check('standard_closed_initially',abs(front.get_open_angle())<.1);key('E');s.update(phase=2,next=now+5);return
  if s['phase']==2:
   s['door_debug']={'angle':front.get_open_angle(),'prompt_visible':front.get_editor_property('prompt').is_visible(),'prompt':str(front.get_editor_property('prompt').text),'pawn':list(p.get_actor_location().to_tuple()),'door':list(front.get_actor_location().to_tuple()),'leaf_mesh':str(front.leaf.static_mesh),'collision':str(front.leaf_collision.get_collision_enabled())}
   check('E_opens_actual_control_door',front.get_open_angle()>94)
   s['walk_start_y']=p.get_actor_location().y;s.update(phase=3,next=now,until=now+2);return
  if s['phase']==3:
   p.add_movement_input(unreal.Vector(0,-1,0),1,False)
   if now<s['until']:return
   p.character_movement.stop_movement_immediately();check('player_passes_open_control_door',s['walk_start_y']-p.get_actor_location().y>230)
   # Close from the interior after moving clear of the sweep.
   p.set_actor_location(front.get_actor_location()+unreal.Vector(65,-150,98),False,True);front.try_interact();s.update(phase=4,next=now+5);return
  if s['phase']==4:
   check('control_door_closes',abs(front.get_open_angle())<.1)
   secure=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label()=='D03_Transient_Keypad_Test')
   check('keypad_starts_locked',secure.is_locked());check('locked_interaction_refused',not secure.try_interact());check('wrong_code_refused',not secure.submit_code('1111'));check('empty_code_refused',not secure.submit_code(''))
   s.update(phase=5,next=now+1);return
  if s['phase']==5:
   check('locked_leaf_did_not_move',abs(secure.get_open_angle())<.1)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(secure.get_actor_location()+unreal.Vector(65,190,98),False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=-90,pitch=0))
   s.update(phase=6,next=now+.5,entry=['E','Zero','Four','Two','Six','Enter'],entry_index=0);return
  if s['phase']==6:
   if s['entry_index']<len(s['entry']):
    key(s['entry'][s['entry_index']]);s['entry_index']+=1;s['next']=now+.2;return
   check('keyboard_code_unlocks',not secure.is_locked());check('unlocked_interaction_accepted',secure.try_interact());s.update(phase=7,next=now+5);return
  if s['phase']==7:
   check('keypad_door_opens_after_code',secure.get_open_angle()>94)
   # Put the actual capsule in the closing sweep; it must stop before penetrating.
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   p.set_actor_location(secure.get_actor_location()+unreal.Vector(65,35,110),False,True);p.character_movement.stop_movement_immediately();secure.try_interact();s.update(phase=8,next=now+2);return
  if s['phase']==8:
   check('closing_stops_for_player',secure.get_open_angle()>5)
   s['final_angles']={'control':front.get_open_angle(),'obstructed_keypad':secure.get_open_angle()};finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
