import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'elapsed':0.,'samples':0,'deadline':time.monotonic()+70}
def finish(error=None):
 unreal.unregister_slate_post_tick_callback(handle)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s['success']=error is None;s['error']=error
 (out/'platform_peek_runtime.json').write_text(json.dumps(s,indent=2))
 ls.editor_request_end_play()
def tick(dt):
 global p,pc,origin
 try:
  assert time.monotonic()<s['deadline'],'PIE timeout'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p or not pc:return
  s['elapsed']+=dt;s['samples']+=1
  assert not pc.is_move_input_ignored() and not pc.is_look_input_ignored(),'Opening holds input'
  if s['phase']==0:
   origin=p.get_actor_location()
   expected=json.loads((out/'platform_peek_start.json').read_text())['location']
   s['spawn']=[origin.x,origin.y,origin.z]
   assert (origin-unreal.Vector(*expected)).length()<50,'Wrong spawn point'
   s['phase']=1
  if s['phase']==1 and s['elapsed']>=1.0:
   assert p.character_movement.is_moving_on_ground(),'Spawn must settle on platform'
   s['grounded']=True;s['phase']=2;s['move_until']=s['elapsed']+.3;origin=p.get_actor_location()
  if s['phase']==2:
   if s['elapsed']<s['move_until']:
    p.add_movement_input(unreal.MathLibrary.get_forward_vector(pc.get_control_rotation()),1.,False)
   else:
    s['walk_cm']=(p.get_actor_location()-origin).length();assert s['walk_cm']>10,'Movement must work immediately'
    p.character_movement.stop_movement_immediately();s['phase']=3
  if s['phase']==3 and s['elapsed']>6.5:
   assert p.character_movement.is_moving_on_ground(),'Player fell off platform'
   ds=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)
   assert ds and all(d.get_editor_property('peek_yaw_degrees')==65 for d in ds)
   s['peek_degrees']=65;s['input_unlocked_through_opening']=True
   finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick)
ls.editor_request_begin_play()
RESULT={'testing':True}
