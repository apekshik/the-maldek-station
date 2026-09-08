"""PIE checks of the installed code 1234 doors and actual player passage at relay."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+180,'checks':{}}
labels=['R12_Door_Control_front','R12_Door_Relay_north','R12_Door_Relay_south']
def check(n,v):s['checks'][n]=bool(v);assert v,n
def key(k):unreal.StationMigrationLibrary.send_pie_key(k,True);unreal.StationMigrationLibrary.send_pie_key(k,False)
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(success=error is None,error=error);(out/'keypad_runtime.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global doors,p,pc,d,start,direction
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};check('four_installed_doors',len(doors)==4)
   side=doors['R12_Door_Control_side'];check('control_side_standard',not side.has_keypad and not side.is_locked());s['phase']=1
  if s['phase']==1:
   if s['index']==len(labels):finish();return
   d=doors[labels[s['index']]];check(d.get_actor_label()+'_locked_with_1234',d.is_locked() and d.access_code=='1234');check(d.get_actor_label()+'_wrong_code_rejected',not d.submit_code('9999'));check(d.get_actor_label()+'_locked_open_refused',not d.try_interact())
   t=d.get_actor_transform();pos=unreal.MathLibrary.transform_location(t,unreal.Vector(65,190,102/d.get_actor_scale3d().z));p.set_actor_location(pos,False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90,pitch=0))
   s.update(phase=2,next=now+2,entry=['E','One','Two','Three','Four','Enter'],entry_index=0);return
  if s['phase']==2:
   if s['entry_index']<len(s['entry']):key(s['entry'][s['entry_index']]);s['entry_index']+=1;s['next']=now+.3;return
   check(d.get_actor_label()+'_keyboard_1234_unlocks',not d.is_locked());check(d.get_actor_label()+'_open_accepted',d.try_interact());s.update(phase=3,next=now+5);return
  if s['phase']==3:
   s[d.get_actor_label()+'_angle']=d.get_open_angle();check(d.get_actor_label()+'_opens_fully',d.get_open_angle()>94)
   start=p.get_actor_location();direction=unreal.MathLibrary.get_forward_vector(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=4,next=now,until=now+2);return
  if s['phase']==4:
   p.add_movement_input(direction,1,False)
   if now<s['until']:return
   p.character_movement.stop_movement_immediately();delta=p.get_actor_location()-start;travel=delta.x*direction.x+delta.y*direction.y+delta.z*direction.z;s[d.get_actor_label()+'_walk_cm']=travel;check(d.get_actor_label()+'_player_walks_through',travel>230)
   p.set_actor_location(start,False,True);d.try_interact();s.update(phase=5,next=now+5);return
  if s['phase']==5:
   check(d.get_actor_label()+'_closes',abs(d.get_open_angle())<.1);s['index']+=1;s.update(phase=1,next=now+.2)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
