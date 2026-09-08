"""PIE E input and viewport pointer events: cancel, partial drag, seating, egress, traversal."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+360,'checks':{},'rows':[]};pointer=None
def check(n,v):
 s['checks'][d.get_actor_label()+'_'+n]=bool(v);assert v,n
def advance(phase,wait=.2):
 s.update(phase=phase,next=time.monotonic()+wait);(out/'progress.json').write_text(json.dumps(s,indent=2))
def key(k,down):unreal.StationMigrationLibrary.send_pie_key(k,down)
def point(v):
 global pointer
 pointer=v;assert unreal.StationMigrationLibrary.send_pie_mouse_position(v.x,v.y)
def project(q):return pc.project_world_location_to_screen(d.get_key_grip_world_position(q))
def place(side=1,distance=None):
 pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(100 if distance else 65,side*(distance if distance else 80 if d.get_actor_label()=='R12_Door_Quarters' else 150),102/d.get_actor_scale3d().z))
 p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(pos,False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw+(-90 if side>0 else 90)))
def finish(error=None):
 key('LeftMouseButton',False);key('E',False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc,doors,labels,pointer,start,direction
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
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720);doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};labels=sorted(n for n,a in doors.items() if a.has_key_lock);assert len(labels)==7
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   advance(1);return
  if phase==1:
   if s['index']==len(labels):finish();return
   d=doors[labels[s['index']]];check('starts_key_locked',d.is_locked() and not d.has_keypad);place();advance(2,.7);return
  if phase==2:key('E',True);advance(3,.15);return
  if phase==3:key('E',False);advance(4,.8);return
  if phase==4:
   check('inspection_fill_on',d.key_inspection_light.is_visible())
   mi=d.interaction_prompt.get_material_instance();s['prompt_material']={'material':d.interaction_prompt.get_material(0).get_path_name(),'parent':mi.get_editor_property('parent').get_path_name() if mi else None}
   check('E_enters_key_camera',d.is_using_key() and pc.get_view_target()==d);check('input_held',pc.is_move_input_ignored() and pc.is_look_input_ignored());check('door_still_shut',abs(d.get_open_angle())<.01)
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/(d.get_actor_label()+'_key.png'))+'"');point(project(0)+unreal.Vector2D(-100,-100));key('LeftMouseButton',True);advance(5);return
  if phase==5:point(project(1));advance(6);return
  if phase==6:
   check('off_key_drag_rejected',d.get_key_insertion()<.001);key('LeftMouseButton',False);point(project(0));advance(7);return
  if phase==7:s['pointer_probe']={'expected':str(pointer),'read':str(pc.get_mouse_position()),'viewport':str(pc.get_viewport_size())};key('LeftMouseButton',True);advance(8);return
  if phase==8:
   check('click_alone_does_not_insert',d.get_key_insertion()<.001);point(project(.45));advance(9);return
  if phase==9:
   s['last_partial']=d.get_key_insertion();check('mouse_partial_insertion',abs(d.get_key_insertion()-.45)<.04);key('LeftMouseButton',False);advance(10);return
  if phase==10:point(project(1));advance(11);return
  if phase==11:
   check('release_holds_partial',abs(d.get_key_insertion()-.45)<.04);point(project(.45));advance(12);return
  if phase==12:key('LeftMouseButton',True);advance(13);return
  if phase==13:point(project(.2));advance(14);return
  if phase==14:
   check('drag_can_reverse',abs(d.get_key_insertion()-.2)<.04);key('LeftMouseButton',False);key('E',True);advance(15,.15);return
  if phase==15:key('E',False);pointer=None;advance(16,.6);return
  if phase==16:
   check('cancel_stays_locked',d.is_locked() and not d.is_using_key() and d.get_key_insertion()==0);check('cancel_restores_input',pc.get_view_target()==p and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());key('E',True);advance(17,.15);return
  if phase==17:key('E',False);advance(18,.8);return
  if phase==18:check('reentry',d.is_using_key());point(project(0));advance(19);return
  if phase==19:key('LeftMouseButton',True);advance(20);return
  if phase==20:s['drag_step']=1;advance(21);return
  if phase==21:
   point(project(s['drag_step']/8));s['drag_step']+=1
   if s['drag_step']<=8:advance(21,.08)
   else:advance(22,.2)
   return
  if phase==22:
   check('recorded_turn_playing',d.key_turn_sound and d.get_editor_property('EventAudio').sound==d.key_turn_sound and d.get_editor_property('EventAudio').is_playing())
   check('seated_before_unlock',d.get_key_insertion()>.99 and d.is_locked());key('LeftMouseButton',False);pointer=None;advance(23,1.6);return
  if phase==23:
   check('inspection_fill_off',not d.key_inspection_light.is_visible())
   check('seating_unlocks',not d.is_locked());check('unlock_leaves_door_shut',abs(d.get_open_angle())<.01);check('unlock_restores_input',not d.is_using_key() and pc.get_view_target()==p and not pc.is_move_input_ignored());check('unlock_sound',d.get_editor_property('LockAudio').sound==d.unlock_sound)
   if d.get_actor_scale3d().x>1.1 and d.open_angle>0:place(distance=205)
   advance(23.5,.5);return
  if phase==23.5:s['open_focus']={'visible':d.interaction_prompt.is_visible(),'camera':str(unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location()),'pawn':str(p.get_actor_location())};key('E',True);advance(24,.15);return
  if phase==24:key('E',False);advance(25,1.8);return
  if phase==25:
   check('E_opens_after_unlock',abs(d.get_open_angle())>94);s['rows'].append({'label':d.get_actor_label(),'angle':d.get_open_angle()})
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,80,98/d.get_actor_scale3d().z)),False,True);start=p.get_actor_location();direction=unreal.MathLibrary.get_forward_vector(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s['walk_until']=now+1.2;advance(26,0);return
  if phase==26:
   p.add_movement_input(direction,1,False)
   if now<s['walk_until']:return
   p.character_movement.stop_movement_immediately();delta=p.get_actor_location()-start;travel=delta.x*direction.x+delta.y*direction.y;s['rows'][-1]['walk_cm']=travel;check('player_traversal',travel>120);place(distance=230);d.try_interact();advance(27,2);return
  if phase==27:
   check('closed_relocks',d.is_locked() and abs(d.get_open_angle())<.01);d.set_editor_property('key_available',False);place();advance(28,.5);return
  if phase==28:key('E',True);advance(29,.15);return
  if phase==29:key('E',False);advance(30,.5);return
  if phase==30:
   check('missing_key_gate',d.is_locked() and not d.is_using_key());place(-1);advance(31,.5);return
  if phase==31:key('E',True);advance(32,.15);return
  if phase==32:key('E',False);advance(33,1.8);return
  if phase==33:
   s['inside_result']={'locked':d.is_locked(),'key_mode':d.is_using_key(),'angle':d.get_open_angle(),'pawn':str(p.get_actor_location())};check('inside_egress_without_key',not d.is_locked() and not d.is_using_key() and abs(d.get_open_angle())>.1);d.set_editor_property('key_available',True);s['index']+=1;advance(1);return
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
