"""Actual E/pointer key use, cancellation, audio, swing and capsule crossing in PIE."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];out=OUT/'doors';shots=OUT/'previews/doors_runtime';shots.mkdir(exist_ok=True);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+12,'deadline':time.monotonic()+360,'checks':{},'rows':[],'busy':False};pointer=None
def check(n,v):s['checks'][d.get_actor_label()+'_'+n]=bool(v);assert v,n
def advance(phase,wait=.2):s.update(phase=phase,next=time.monotonic()+wait)
def key(k,down):unreal.StationMigrationLibrary.send_pie_key(k,down) # Return value is event consumption, not delivery.
def point(v):
 global pointer
 pointer=v;assert unreal.StationMigrationLibrary.send_pie_mouse_position(v.x,v.y)
def project(q):return pc.project_world_location_to_screen(d.get_key_grip_world_position(q))
def world(p):return unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(*p))
def place(interior=False):
 side=(1 if d.interior_is_negative_y else -1)*(-1 if interior else 1);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.character_movement.stop_movement_immediately();p.set_actor_location(world([row['width']*50+6,side*150,99]),False,True);eye=p.get_actor_location()+unreal.Vector(0,0,64);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,world([row['width']*50+6,0,110])))
def shot(name):
 path=shots/(d.get_actor_label()+'_'+name+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path));s.setdefault('images',[]).append(str(path))
def finish(error=None):
 unreal.StationMigrationLibrary.send_pie_key('LeftMouseButton',False);unreal.StationMigrationLibrary.send_pie_key('E',False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(out/'runtime.json').write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc,doors,labels,pointer,row,start,target
 if s['busy']:return
 s['busy']=True
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
   unreal.StationMigrationLibrary.set_pie_render_size(1600,1000);doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};labels=['MIG_PLD_ARRIVAL','MIG_PLD_GONDOLA','MIG_PLD_STAFF'];assert all(n in doors for n in labels)
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   torch=p.get_components_by_class(unreal.SpotLightComponent)[0]
   if not torch.is_visible():p.toggle_flashlight()
   advance(1);return
  if phase==1:
   if s['index']==len(labels):finish();return
   d=doors[labels[s['index']]];row=next(r for r in json.loads((out/'exports.json').read_text())['doors'] if r['id']==labels[s['index']].replace('MIG_PLD_',''));check('starts_locked',d.is_locked() and d.use_authored_hardware and not d.has_keypad);place();advance(2,.7);return
  if phase==2:shot('closed_night');advance(2.5,1);return
  if phase==2.5:key('E',True);advance(3,.15);return
  if phase==3:key('E',False);advance(4,.8);return
  if phase==4:
   check('E_enters_key_camera',d.is_using_key() and pc.get_view_target()==d);check('input_held',pc.is_move_input_ignored() and pc.is_look_input_ignored());shot('key_ready');advance(4.5,1);return
  if phase==4.5:point(project(0)+unreal.Vector2D(-350,-250));key('LeftMouseButton',True);advance(5);return
  if phase==5:point(project(1));advance(6);return
  if phase==6:check('off_key_drag_rejected',d.get_key_insertion()<.001);key('LeftMouseButton',False);point(project(0));advance(7);return
  if phase==7:key('LeftMouseButton',True);advance(8);return
  if phase==8:check('click_alone_does_not_insert',d.get_key_insertion()<.001);point(project(.45));advance(9);return
  if phase==9:check('partial_insertion',abs(d.get_key_insertion()-.45)<.04);key('LeftMouseButton',False);advance(10);return
  if phase==10:point(project(1));advance(11);return
  if phase==11:check('release_holds_partial',abs(d.get_key_insertion()-.45)<.04);point(project(.45));advance(12);return
  if phase==12:key('LeftMouseButton',True);advance(13);return
  if phase==13:point(project(.2));advance(14);return
  if phase==14:check('reverse_drag',abs(d.get_key_insertion()-.2)<.04);key('LeftMouseButton',False);key('E',True);advance(15,.15);return
  if phase==15:key('E',False);pointer=None;advance(16,.6);return
  if phase==16:
   check('cancel_stays_locked',d.is_locked() and not d.is_using_key() and d.get_key_insertion()==0);check('cancel_restores_input',pc.get_view_target()==p and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());key('E',True);advance(17,.15);return
  if phase==17:key('E',False);advance(18,.8);return
  if phase==18:check('reentry',d.is_using_key());point(project(0));advance(19);return
  if phase==19:key('LeftMouseButton',True);advance(20);return
  if phase==20:s['drag_step']=1;advance(21);return
  if phase==21:
   point(project(s['drag_step']/8));s['drag_step']+=1;advance(21 if s['drag_step']<=8 else 22,.08 if s['drag_step']<=8 else .2);return
  if phase==22:
   check('recorded_turn_playing',d.key_turn_sound and d.get_editor_property('EventAudio').sound==d.key_turn_sound and d.get_editor_property('EventAudio').is_playing());check('seated_before_unlock',d.get_key_insertion()>.99 and d.is_locked());check('plug_turns',abs(d.key_plug.get_relative_transform().rotation.rotator().pitch)>1);shot('turning_key');key('LeftMouseButton',False);pointer=None;advance(23,1.7);return
  if phase==23:
   check('unlock_shut',not d.is_locked() and abs(d.get_open_angle())<.01);check('unlock_restores_input',not d.is_using_key() and pc.get_view_target()==p and not pc.is_move_input_ignored());key('E',True);advance(24,.15);return
  if phase==24:key('E',False);advance(24.5,.3);return
  if phase==24.5:
   check('latch_retracted',d.moving_latch.get_relative_transform().translation.x<-.5);check('seal_lifted',d.bottom_seal.get_relative_transform().translation.z>.5);check('lever_depressed',abs(d.front_lever.get_relative_transform().rotation.rotator().pitch)>1);check('movement_audio',d.get_editor_property('MotionAudio').is_playing());advance(25,1.7);return
  if phase==25:
   angle=d.get_open_angle();s['rows'].append({'label':d.get_actor_label(),'angle':angle});check('full_swing',abs(angle-row['open_angle'])<.1);shot('open_night');advance(25.5,1);return
  if phase==25.5:
   side=1 if d.interior_is_negative_y else -1;p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.character_movement.max_walk_speed=180;p.set_actor_location(world([row['width']*50+6,side*80,99]),False,True);start=p.get_actor_location();target=world([row['width']*50+6,-side*80,99]);s['walk_start']=now;advance(26,.7);return
  if phase==26:
   delta=target-p.get_actor_location();delta.z=0
   if delta.length()>12:
    assert now-s['walk_start']<12,'walking stalled';p.add_movement_input(delta/delta.length(),min(1,max(.2,delta.length()/80)),True);return
   foot=p.get_actor_location().z-p.capsule_component.get_scaled_capsule_half_height()-d.get_actor_location().z;check('capsule_crossing',abs(foot)<8);p.character_movement.stop_movement_immediately();s['rows'][-1]['crossing_distance_cm']=(p.get_actor_location()-start).length();place();d.try_interact();advance(27,2);return
  if phase==27:
   check('closed_relocks',d.is_locked() and abs(d.get_open_angle())<.01);d.set_editor_property('key_available',False);place();advance(28,.5);return
  if phase==28:key('E',True);advance(29,.15);return
  if phase==29:key('E',False);advance(30,.5);return
  if phase==30:check('missing_key_gate',d.is_locked() and not d.is_using_key());place(True);advance(31,.5);return
  if phase==31:key('E',True);advance(32,.15);return
  if phase==32:key('E',False);advance(33,2);return
  if phase==33:
   check('inside_egress_without_key',not d.is_locked() and not d.is_using_key() and abs(d.get_open_angle()-row['open_angle'])<.1);d.set_editor_property('key_available',True);place();d.try_interact();advance(34,2);return
  if phase==34:
   check('rest_pose',d.is_locked() and abs(d.get_open_angle())<.01);s['index']+=1;advance(1);return
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
