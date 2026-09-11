import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+2,'deadline':time.monotonic()+85,'checks':{}}
pointer=None
def key(k,v):unreal.StationMigrationLibrary.send_pie_key(k,v)
def step(n,t=1):s['phase']=n;s['next']=time.monotonic()+t
def check(k,v):s['checks'][k]=bool(v);assert v,k
def finish(error=None):
 for k in ['Q','E','LeftMouseButton']:key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s.update(success=error is None,error=error);(out/'peek_narrow_runtime.json').write_text(json.dumps(s,indent=2));ls.editor_request_end_play()
def delta(a,b):return (a-b+180)%360-180
def tick(dt):
 global d,p,pc,cam,beam,parent,restyaw,restroll,facing,mouse,beamrest,pointer
 try:
  if pointer:unreal.StationMigrationLibrary.send_pie_mouse_position(*pointer)
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
   beam=p.get_components_by_class(unreal.SpotLightComponent)[0];parent=beam.get_attach_parent();r=beam.get_editor_property('relative_rotation');beamrest=(float(r.pitch),float(r.yaw),float(r.roll))
   if not beam.is_visible():p.toggle_flashlight()
   s['beam_intensity']=beam.intensity;s['beam_cone']=beam.outer_cone_angle
   width,height=pc.get_viewport_size();pointer=(width/2,height/2)
   step(1,.5)
  elif n==1:d.try_interact();step(2)
  elif n==2:
   check('entered',d.is_using_key());cam=d.get_editor_property('KeypadCamera');r=cam.get_editor_property('relative_rotation');restyaw=float(r.yaw);restroll=float(r.roll)
   facing=float(d.key_lock_root.get_editor_property('relative_rotation').yaw)-90
   check('torch_normal_until_peek',beam.get_attach_parent()==parent)
   mouse=pc.get_mouse_position() or pointer;key('Q',True);step(3)
  elif n==3:
   check('left_from_face_95',abs(delta(cam.get_editor_property('relative_rotation').yaw,facing)+95)<.2);check('peek_uses_tightest_beam',abs(beam.outer_cone_angle-11)<.01);check('beam_follows_peek',beam.get_attach_parent()==cam)
   width,height=pc.get_viewport_size();pointer=(mouse[0]+width*.2,mouse[1]-height*.15);unreal.StationMigrationLibrary.send_pie_mouse_position(*pointer)
   key('LeftMouseButton',True);step(4,.04)
  elif n==4:
   r=beam.get_editor_property('relative_rotation');s['aim']={'yaw':r.yaw,'pitch':r.pitch}
   check('aim_has_no_added_lag',abs(r.yaw-16)<.3 and abs(r.pitch-9)<.3);check('beam_aim_limited',abs(r.yaw)<=24.1 and abs(r.pitch)<=18.1)
   check('camera_stays_at_peek',abs(delta(cam.get_editor_property('relative_rotation').yaw,facing)+95)<.2)
   check('aim_does_not_insert_key',d.get_key_insertion()==0)
   check('narrow_focus_stays_active',abs(beam.outer_cone_angle-11)<.01)
   check('no_lock_fill_during_peek',not d.key_inspection_light.is_visible())
   pointer=None;key('LeftMouseButton',False);key('Q',False);step(5,1.3)
  elif n==5:
   check('returns_to_oblique_view',abs(delta(cam.get_editor_property('relative_rotation').yaw,restyaw))<.2)
   r=beam.get_editor_property('relative_rotation');check('normal_beam_restored_on_release',abs(beam.outer_cone_angle-s['beam_cone'])<.01 and abs(beam.intensity-s['beam_intensity'])<.01);check('torch_restored_to_player',beam.get_attach_parent()==parent)
   s['cursor_after_synthetic_input']={'expected':mouse,'actual':pc.get_mouse_position()};pointer=mouse
   key('E',True);step(6)
  elif n==6:
   check('right_from_face_95',abs(delta(cam.get_editor_property('relative_rotation').yaw,facing)-95)<.2)
   check('fov_preserved',abs(cam.field_of_view-85)<.1)
   key('E',False);d.cancel_keypad_interaction();step(7,.5)
  elif n==7:
   check('torch_parent_restored',beam.get_attach_parent()==parent);check('normal_beam_restored_on_cancel',abs(beam.outer_cone_angle-s['beam_cone'])<.01 and abs(beam.intensity-s['beam_intensity'])<.01)
   r=beam.get_editor_property('relative_rotation');check('torch_rotation_restored',abs(delta(r.pitch,beamrest[0]))<.1 and abs(delta(r.yaw,beamrest[1]))<.1)
   check('input_restored',not pc.is_move_input_ignored() and not pc.is_look_input_ignored());finish()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'testing':True}




