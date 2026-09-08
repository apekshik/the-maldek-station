"""Exercise camera entry/cancel and actual projected mouse clicks on all installed keypads."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'audio_review';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+180,'checks':{},'sound_events':[]}
labels=['R12_Door_Control_front','R12_Door_Relay_north','R12_Door_Relay_south']
def check(n,v):s['checks'][n]=bool(v);assert v,n
def key(k):unreal.StationMigrationLibrary.send_pie_key(k,True);unreal.StationMigrationLibrary.send_pie_key(k,False)
def finish(error=None):
 if s.get('recording'):
  unreal.AudioMixerLibrary.stop_recording_output(unreal.EditorLevelLibrary.get_game_world(),unreal.AudioRecordingExportType.WAV_FILE,'door_and_keypad_mix',str(out));s['recording']=False
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(success=error is None,error=error);(out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.StationMigrationLibrary.set_pie_render_size(0,0);unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global p,pc,d,doors,start,view
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    if not isinstance(a,unreal.StationDoor):
     for c in a.get_components_by_class(unreal.AudioComponent):c.stop()
   unreal.AudioMixerLibrary.start_recording_output(w,100);s['recording']=True
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};s['phase']=1
  if s['phase']==1:
   if s['index']==len(labels):finish();return
   d=doors[labels[s['index']]];pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,190,102/d.get_actor_scale3d().z));p.set_actor_location(pos,False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=2,next=now+2);return
  if s['phase']==2:key('E');s.update(phase=3,next=now+1.5);return
  if s['phase']==3:
   check(d.get_actor_label()+'_camera_entered',d.is_using_keypad() and pc.get_view_target()==d);check(d.get_actor_label()+'_movement_locked',pc.is_move_input_ignored() and pc.is_look_input_ignored());view=unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location();key('E' if s['index']==0 else 'RightMouseButton');s.update(phase=4,next=now+1);return
  if s['phase']==4:
   check(d.get_actor_label()+'_cancel_restores_player',not d.is_using_keypad() and pc.get_view_target()==p and not pc.is_move_input_ignored() and not pc.is_look_input_ignored());check(d.get_actor_label()+'_cancel_keeps_locked',d.is_locked());key('E');s.update(phase=5,next=now+1.5);return
  if s['phase']==5:
   check(d.get_actor_label()+'_reentry',d.is_using_keypad());file=out/(d.get_actor_label()+'.png');file.unlink(missing_ok=True);unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename='+str(file));s.update(phase=6,next=now+.5,clicks=[8,11,0,1,9,0,1,2,3,11],click_index=0);return
  if s['phase']==6:
   if s['click_index']>0:
    previous=s['clicks'][s['click_index']-1];expected='KeyClear' if previous==9 else 'KeyReject' if previous==11 and s['click_index']==2 else 'KeyConfirm' if previous==11 else 'KeyPress';actual=d.get_editor_property('EventAudio').sound.get_name();s['sound_events'].append(actual);check(d.get_actor_label()+'_sound_'+str(s['click_index']),actual==expected)
   if s['click_index']==len(s['clicks']):s.update(phase=8,next=now+1);return
   i=s['clicks'][s['click_index']];screen=pc.project_world_location_to_screen(d.get_keypad_button_world_position(i));s['last_projection']=str(screen);pc.set_mouse_location(int(screen.x),int(screen.y));s.update(phase=7,next=now+.2);return
  if s['phase']==7:
   key('LeftMouseButton');s['click_index']+=1;s.update(phase=6,next=now+.35)
   if s['click_index']==2:check(d.get_actor_label()+'_wrong_click_code_stays_locked',d.is_locked())
   return
  if s['phase']==8:
   check(d.get_actor_label()+'_mouse_1234_unlocks',not d.is_locked());check(d.get_actor_label()+'_unlock_restores_player',not d.is_using_keypad() and pc.get_view_target()==p and not pc.is_move_input_ignored());d.try_interact();s.update(phase=9,next=now+3);return
  if s['phase']==9:
   check(d.get_actor_label()+'_door_opens_after_closeup',d.get_open_angle()>94);d.try_interact();s.update(phase=10,next=now+3);return
  if s['phase']==10:
   check(d.get_actor_label()+'_close_sound',d.get_editor_property('EventAudio').sound==d.close_sound);check(d.get_actor_label()+'_motion_audio_stopped',not d.get_editor_property('MotionAudio').is_playing());s['index']+=1;s.update(phase=1,next=now+.2)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
