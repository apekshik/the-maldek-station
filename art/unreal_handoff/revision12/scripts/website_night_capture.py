import unreal,time,json,traceback
from pathlib import Path
out=Path('C:/Users/apek-anna/Documents/ChatGPT/maldek-station/.local/fresh-captures');out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor(), 'Existing play session must be left untouched'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
shots=[('platform',[-44282.305975,18799.707568,10463.5],[-44282.305975,22327.707568,10468.5]),('gondola',[-44082.305975,18679.707568,10463.5],[-44282.305975,19279.707568,10468.5])]
s={'phase':'place','index':0,'next':time.monotonic()+15,'deadline':time.monotonic()+180,'busy':False}
def finish():
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();settings.set_editor_property('bThrottleCPUWhenNotForeground',old);(out/'report.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'],'Capture timed out'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if s['phase']=='place':
   unreal.StationMigrationLibrary.set_pie_render_size(2560,1440)
   for cmd in ['stat none','r.MotionBlurQuality 0','r.DepthOfFieldQuality 0'] :unreal.SystemLibrary.execute_console_command(w,cmd)
   p.character_movement.stop_movement_immediately();p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True)
   name,eye,target=shots[s['index']];p.set_actor_location(unreal.Vector(*eye)-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*eye),unreal.Vector(*target)))
   s.update(phase='capture',next=time.monotonic()+18)
  elif s['phase']=='capture':
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/(shots[s['index']][0]+'.png')));s['index']+=1;s.update(phase='place' if s['index']<len(shots) else 'finish',next=time.monotonic()+4)
  else:s['success']=True;finish()
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
