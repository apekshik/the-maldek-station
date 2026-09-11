"""Capture the standard and keypad hints without the introductory tutorial overlay."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'recorded_audio'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+9,'deadline':time.monotonic()+60}
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s.update(success=error is None,error=error);(out/'ui.json').write_text(json.dumps(s,indent=2))
 unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc
 now=time.monotonic()
 if now<s['next']:return
 try:
  assert now<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  if s['phase']==0:
   p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
   if not p:return
   opening=p.get_component_by_class(unreal.StationOpeningComponent)
   widget=opening.get_editor_property('Widget')
   if widget:widget.remove_from_parent()
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};d=doors['R12_Door_Control_front']
   p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,145,102/d.get_actor_scale3d().z)),False,True)
   p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=1,next=now+4);return
  if s['phase']==1:
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename='+str(out/'clean_door_hint.png'))
   unreal.StationMigrationLibrary.send_pie_key('E',True);unreal.StationMigrationLibrary.send_pie_key('E',False);s.update(phase=2,next=now+1.5);return
  if s['phase']==2:
   assert d.is_using_keypad();unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename='+str(out/'clean_keypad_hint.png'));s.update(phase=3,next=now+.8);return
  if s['phase']==3:finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
