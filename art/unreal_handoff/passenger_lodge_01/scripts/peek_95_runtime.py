import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+2,'deadline':time.monotonic()+70,'checks':{}}
def key(k,v):unreal.StationMigrationLibrary.send_pie_key(k,v)
def step(n,t=1):s['phase']=n;s['next']=time.monotonic()+t
def check(k,v):s['checks'][k]=bool(v);assert v,k
def finish(error=None):
 for k in ['Q','E']:key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s.update(success=error is None,error=error);(out/'peek_95_runtime_verified.json').write_text(json.dumps(s,indent=2));ls.editor_request_end_play()
def delta(a,b):return (a-b+180)%360-180
def tick(dt):
 global d,p,pc,cam,rest,restyaw,restroll
 try:
  if time.monotonic()<s['next']:return
  assert time.monotonic()<s['deadline'],'timeout'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  n=s['phase']
  if n==0:
   d=next(d for d in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if d.get_actor_label()=='MIG_PLD_ARRIVAL')
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,150 if d.interior_is_negative_y else -150,99));p.set_actor_location(pos,False,True)
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,0,110))))
   step(1,.5)
  elif n==1:d.try_interact();step(2,.15)
  elif n==2:key('E',False);step(3)
  elif n==3:
   check('key_interaction_entered',d.is_using_key());cam=d.get_editor_property('KeypadCamera');rest=cam.get_editor_property('relative_rotation');restyaw=float(rest.yaw);restroll=float(rest.roll)
   check('center_fov',abs(cam.field_of_view-56)<.1);key('Q',True);step(4)
  elif n==4:
   r=cam.get_editor_property('relative_rotation');s['left_probe']={'yaw':r.yaw,'rest':restyaw,'roll':r.roll,'fov':cam.field_of_view};check('left_95',abs(delta(r.yaw,restyaw)+95)<.2);check('left_tilt_8',abs(delta(r.roll,restroll)+8)<.2);check('peek_fov_85',abs(cam.field_of_view-85)<.1)
   key('Q',False);step(5)
  elif n==5:
   check('release_recenters',abs(delta(cam.get_editor_property('relative_rotation').yaw,restyaw))<.2);check('release_restores_fov',abs(cam.field_of_view-56)<.1)
   key('E',True);step(6)
  elif n==6:
   check('right_95',abs(delta(cam.get_editor_property('relative_rotation').yaw,restyaw)-95)<.2);check('right_tilt_8',abs(delta(cam.get_editor_property('relative_rotation').roll,restroll)-8)<.2)
   key('E',False);d.cancel_keypad_interaction();step(7,.5)
  elif n==7:
   check('exit_restores_fov',abs(cam.field_of_view-56)<.1);check('exit_restores_input',not pc.is_move_input_ignored() and not pc.is_look_input_ignored());finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'testing':True}





