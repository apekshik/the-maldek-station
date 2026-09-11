import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ls.editor_request_end_play()
state={'frames':0}
def install(dt):
 state['frames']+=1
 if state['frames']<10 or ls.is_in_play_in_editor():return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
  assert 'Station_Lodge_Migration' in w.get_path_name()
  actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
  starts=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.PlayerStart)
  assert len(starts)==1
  start=starts[0]
  d=next(d for d in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if d.get_actor_label()=='R12_Door_Control_front')
  p=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(-150,100,0))
  hit=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,200),p-unreal.Vector(0,0,1500),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
  h=hit.to_tuple() if hit else None
  assert h and h[0], 'Platform floor must have collision: '+str(p)+' '+str(h)
  floor=h[4]
  assert abs(floor.z-p.z)<50, str(h)
  pos=unreal.Vector(p.x,p.y,floor.z+100)
  target=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,0,164))
  rotation=unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),target)
  marker=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Parking_OriginalStart'),None)
  if not marker:
   marker=actors.spawn_actor_from_class(unreal.TargetPoint,start.get_actor_location(),start.get_actor_rotation())
   marker.set_actor_label('Parking_OriginalStart')
  start.set_actor_location(pos,False,True);start.set_actor_rotation(rotation,False);start.set_actor_label('Platform_Peek_TestStart')
  assert ls.save_current_level()
  (out/'platform_peek_start.json').write_text(json.dumps({'success':True,'location':[pos.x,pos.y,pos.z],'floor':str(floor),'floor_actor':h[9].get_actor_label() if h[9] else None,'rotation':str(rotation)},indent=2))
 except Exception:
  import traceback
  (out/'platform_peek_start.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}))
handle=unreal.register_slate_post_tick_callback(install)
RESULT={'installing':True}



