import unreal,json,time,traceback,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+10,'deadline':time.monotonic()+300,'results':[],'busy':False}
def advance(n,t=.15):s.update(phase=n,next=time.monotonic()+t)
def finish(error=None):
 unreal.StationMigrationLibrary.send_pie_key('E',False);settings.set_editor_property('bThrottleCPUWhenNotForeground',old);(P/'focus_runtime.json').write_text(json.dumps({'error':error,'results':s['results'],'passed':error is None and len(s['results'])==17},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def aim(a):
 target=unreal.MathLibrary.transform_location(a.pivot.get_world_transform(),a.focus_location)
 for dz in [35,0,65,-25]:
  for i in range(16):
   candidate=([35,0,65,-25].index(dz)*16+i)
   if candidate<s.get('candidate',0):continue
   eye=target+unreal.Vector(125*math.cos(i*math.pi/8),125*math.sin(i*math.pi/8),dz)
   hit=unreal.SystemLibrary.line_trace_single(w,eye,target,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],unreal.DrawDebugTrace.NONE,True)
   if hit and hit.to_tuple()[0] and hit.to_tuple()[9]==a:
    s['candidate']=candidate+1;p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,target));return
 raise AssertionError('No visible focus ray: '+a.get_actor_label())
def tick(dt):
 global w,p,pc,actors,a
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   actors=sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet) if a.get_actor_label().startswith('MIG_WS_')],key=lambda a:a.get_actor_label())
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   pc.set_ignore_move_input(False);pc.set_ignore_look_input(False);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_enable_collision(False);advance(1);return
  if s['index']==len(actors):finish();return
  a=actors[s['index']]
  if phase==1:
   if 'Secure_tray' in a.get_actor_label():
    door=next(x for x in actors if x.get_actor_label()=='MIG_WS_WSP_Secure_door_hinge')
    if door.get_open_fraction()<.99:door.try_interact();advance(1,2);return
   aim(a);advance(1.5,.3)
  elif phase==1.5:
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location(),unreal.MathLibrary.transform_location(a.pivot.get_world_transform(),a.focus_location)));advance(2,.3)
  elif phase==2:
   if not a.interaction_prompt.is_visible():aim(a);advance(1.5,.3);return
   cam=unreal.GameplayStatics.get_player_camera_manager(w,0);eye=cam.get_camera_location();h=unreal.SystemLibrary.line_trace_single(w,eye,eye+unreal.MathLibrary.get_forward_vector(cam.get_camera_rotation())*200,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],unreal.DrawDebugTrace.NONE,True);(P/'focus_probe.json').write_text(json.dumps({'actor':a.get_actor_label(),'camera':str(eye),'pawn':str(p.get_actor_location()),'hit':str(h.to_tuple()),'view':str(pc.get_view_target())},indent=2));assert a.interaction_prompt.is_visible(),a.get_actor_label()+' focus';unreal.StationMigrationLibrary.send_pie_key('E',True);advance(3)
  elif phase==3:unreal.StationMigrationLibrary.send_pie_key('E',False);advance(4,2)
  elif phase==4:
   s['candidate']=0;assert a.get_open_fraction()>.999,(a.get_actor_label(),'E open',a.get_open_fraction());aim(a);advance(4.5,.3)
  elif phase==4.5:
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location(),unreal.MathLibrary.transform_location(a.pivot.get_world_transform(),a.focus_location)));advance(5,.3)
  elif phase==5:
   if not a.interaction_prompt.is_visible():aim(a);advance(4.5,.3);return
   assert a.interaction_prompt.is_visible(),a.get_actor_label()+' open focus';unreal.StationMigrationLibrary.send_pie_key('E',True);advance(6)
  elif phase==6:unreal.StationMigrationLibrary.send_pie_key('E',False);advance(7,2)
  else:
   assert a.get_open_fraction()<.001,(a.get_actor_label(),'E close',a.get_open_fraction());s['results'].append({'name':a.get_actor_label(),'focus_and_E_open_close':True});s['index']+=1;s['candidate']=0;advance(1)
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
