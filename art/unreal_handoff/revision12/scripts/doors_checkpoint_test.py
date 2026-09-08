"""Exercise actual F6/E/mouse input, louder turn audio and safe checkpoint return."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+2,'deadline':time.monotonic()+70,'checks':{}};pointer=None
def key(k,on):unreal.StationMigrationLibrary.send_pie_key(k,on)
def step(i,wait=.2):s.update(phase=i,next=time.monotonic()+wait)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 key('F6',False);key('E',False);key('LeftMouseButton',False);unreal.StationMigrationLibrary.set_pie_render_size(0,0);unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play();s.update(success=error is None,error=error);(out/'checkpoint_test.json').write_text(json.dumps(s,indent=2))
def tick(dt):
 global pc,p,d,marker,opening,pointer
 try:
  if pointer:unreal.StationMigrationLibrary.send_pie_mouse_position(pointer.x,pointer.y)
  now=time.monotonic()
  if now<s['next']:return
  assert now<s['deadline'],'timeout'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720);d=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label()=='R12_Door_Control_side');marker=unreal.GameplayStatics.get_all_actors_with_tag(w,'DoorTestCheckpoint')[0];opening=p.get_component_by_class(unreal.StationOpeningComponent);check('opening_spawn_retained',(p.get_actor_location()-marker.get_actor_location()).length()>1000);key('F6',True);step(1);return
  if phase==1:key('F6',False);step(2,.7);return
  if phase==2:
   check('F6_returns_to_door',(p.get_actor_location()-marker.get_actor_location()).length()<30);check('tutorial_skipped_safely',opening and not opening.enable_opening and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());check('walking_restored',p.character_movement.movement_mode==unreal.MovementMode.MOVE_WALKING);key('E',True);step(3);return
  if phase==3:key('E',False);step(4,1.2);return
  if phase==4:
   check('checkpoint_faces_usable_lock',d.is_using_key());check('warm_fill_final',abs(d.key_inspection_light.intensity-.08)<.0001 and d.key_inspection_light.is_visible());unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/'checkpoint_key.png')+'"');pointer=pc.project_world_location_to_screen(d.get_key_grip_world_position(0));step(5);return
  if phase==5:key('LeftMouseButton',True);step(6);return
  if phase==6:pointer=pc.project_world_location_to_screen(d.get_key_grip_world_position(1));step(7,.12);return
  if phase==7:
   s['turn_probe']={'insertion':d.get_key_insertion(),'sound':str(d.get_editor_property('EventAudio').sound),'playing':d.get_editor_property('EventAudio').is_playing(),'volume':d.get_editor_property('EventAudio').volume_multiplier,'configured_volume':d.key_turn_volume,'pointer':str(pointer),'mouse':str(pc.get_mouse_position())}
   audio=d.get_editor_property('EventAudio');check('louder_recorded_turn',audio.sound==d.key_turn_sound and audio.is_playing() and abs(audio.volume_multiplier-4)<.01);key('LeftMouseButton',False);pointer=None;key('F6',True);step(8,.1);return
  if phase==8:key('F6',False);step(9,.6);return
  if phase==9:
   check('checkpoint_cancels_turn',d.is_locked() and not d.is_using_key() and not d.get_editor_property('EventAudio').is_playing());check('checkpoint_restores_view_and_input',pc.get_view_target()==p and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());check('checkpoint_turns_fill_off',not d.key_inspection_light.is_visible());check('repeat_return_safe',(p.get_actor_location()-marker.get_actor_location()).length()<30);finish();return
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
