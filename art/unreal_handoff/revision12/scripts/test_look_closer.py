"""Actual right-mouse input and camera-manager FOV regression check in PIE."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'look_closer';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':'start','next':time.monotonic()+10,'checks':{},'samples':[],'busy':False}
def finish():
 unreal.StationMigrationLibrary.send_pie_key('RightMouseButton',False)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s['success']='error' not in s and all(s['checks'].values());(out/'runtime.json').write_text(json.dumps(s,indent=2))
 ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p or not pc:return
  c=p.get_component_by_class(unreal.StationPlayerPresentationComponent);cam=pc.player_camera_manager;now=time.monotonic()
  if s['phase']=='start':
   s['base_fov']=cam.get_fov_angle();s['beam_focus']=c.get_target_focus();s['walk_speed']=p.character_movement.max_walk_speed
   unreal.StationMigrationLibrary.send_pie_key('RightMouseButton',True);s.update(phase='hold',started=now,next=now);return
  if s['phase']=='hold':
   s['samples'].append([now-s['started'],cam.get_fov_angle(),c.get_inspect_amount()])
   if now-s['started']<1.2:return
   s['held_fov']=cam.get_fov_angle();s['checks']['subtle_zoom']=abs(s['base_fov']-s['held_fov']-12)<.05
   s['checks']['smooth_intermediate_frames']=any(.1<a<.9 for _,f,a in s['samples'])
   s['checks']['monotonic_zoom']=all(y[1]<=x[1]+.01 for x,y in zip(s['samples'],s['samples'][1:]))
   s['checks']['beam_unchanged']=c.get_target_focus()==s['beam_focus'];s['checks']['speed_unchanged']=p.character_movement.max_walk_speed==s['walk_speed']
   unreal.StationMigrationLibrary.send_pie_key('RightMouseButton',False);s.update(phase='release',next=now+1.3);return
  if s['phase']=='release':
   s['checks']['release_restores_fov']=abs(cam.get_fov_angle()-s['base_fov'])<.01
   c.set_inspect_active(True);s.update(phase='missed_release',next=now+.5);return
  if s['phase']=='missed_release':
   s['checks']['no_latch_without_button']=c.get_inspect_amount()<.001
   c.set_inspect_active(False);finish()
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
