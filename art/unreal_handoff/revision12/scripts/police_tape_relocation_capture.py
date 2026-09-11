import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();info=json.loads((out/'installation.json').read_text());centre=unreal.Vector(*info['centre_world']);forward=unreal.Vector(*info['forward']);s={'index':0,'phase':'place','next':time.monotonic()+18,'busy':False,'shots':[]};settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
def finish():
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);(out/'relocation/capture.json').write_text(json.dumps(s,indent=2))
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  w=unreal.EditorLevelLibrary.get_game_world();pawn=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not isinstance(pawn,unreal.Character):return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if s['phase']=='place':
   unreal.StationMigrationLibrary.set_pie_render_size(1440,810);pawn.character_movement.stop_movement_immediately();pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
   if s['index']:
    pos=centre-forward*(650 if s['index']==1 else 280);pos.z=info['ground_world_z']+pawn.capsule_component.get_scaled_capsule_half_height()+10;pawn.set_actor_location(pos,False,True)
   s.update(phase='aim',next=time.monotonic()+2)
  elif s['phase']=='aim':
   if s['index']:pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pc.player_camera_manager.get_camera_location(),centre+unreal.Vector(0,0,135)))
   s.update(phase='capture',next=time.monotonic()+4)
  elif s['phase']=='capture':
   name=['spawn','approach','crossing'][s['index']];unreal.AutomationLibrary.take_high_res_screenshot(1440,810,str(out/'relocation'/f'{name}.png'));s['shots'].append(name);s['index']+=1;s.update(phase='end' if s['index']==3 else 'place',next=time.monotonic()+2)
  else:finish()
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
