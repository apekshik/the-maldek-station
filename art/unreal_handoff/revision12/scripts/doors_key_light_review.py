"""Compare the local key inspection fill at the darkest service entrance in PIE."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
s={'phase':0,'next':time.monotonic()+8};levels=[.02,.08,.2];i=0
def tick(dt):
 global d,p,pc,i
 try:
  if time.monotonic()<s['next']:return
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720)
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   d=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label()=='R12_Door_Generator_south')
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,150,102)),False,True);pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=1,next=time.monotonic()+.8);return
  if s['phase']==1:d.try_interact();s.update(phase=2,next=time.monotonic()+.8);return
  if s['phase']==2:
   assert d.is_using_key();d.key_inspection_light.set_intensity(levels[i]);s.update(phase=3,next=time.monotonic()+3);return
  if s['phase']==3:
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/('light_'+str(levels[i])+'.png'))+'"');i+=1;s.update(phase=2 if i<len(levels) else 4,next=time.monotonic()+.5);return
  unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);(out/'light_review.json').write_text(json.dumps({'success':True,'levels':levels}))
 except Exception:
  unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play();(out/'light_review.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}))
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
