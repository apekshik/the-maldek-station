import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'rooms';out.mkdir(exist_ok=True);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+180,'checks':{},'results':[]}
labels=[r['label'] for r in json.loads((out.parent/'rooms_install.json').read_text())['new_doors']]
def key(k):unreal.StationMigrationLibrary.send_pie_key(k,True);unreal.StationMigrationLibrary.send_pie_key(k,False)
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(success=error is None,error=error);(out/'runtime.json').write_text(json.dumps(s,indent=2));unreal.StationMigrationLibrary.set_pie_render_size(0,0);unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc,start,direction,doors
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720);doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};assert len(doors)==10;s['phase']=1
  if s['phase']==1:
   if s['index']==len(labels):
    assert all(abs(r['angle'])>94 and r.get('walk_cm',0)>120 and r.get('closed') and r.get('opening_audio') and r.get('motion_stopped') for r in s['results']);finish();return
   d=doors[labels[s['index']]];assert not d.is_locked() and not d.has_keypad
   pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,80 if d.get_actor_label()=='R12_Door_Quarters' else 205,102/d.get_actor_scale3d().z));p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.set_actor_location(pos,False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=2,next=now+1);return
  if s['phase']==2:
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/(d.get_actor_label()+'_prompt.png'))+'"');s.update(phase=3,next=now+.5);return
  if s['phase']==3:unreal.StationMigrationLibrary.send_pie_key('E',True);s.update(phase=4,next=now+.25);return
  if s['phase']==4:
   unreal.StationMigrationLibrary.send_pie_key('E',False);s['moving_audio']=d.get_editor_property('MotionAudio').is_playing();s.update(phase=5,next=now+3);return
  if s['phase']==5:
   row={'label':d.get_actor_label(),'angle':d.get_open_angle(),'opening_audio':s['moving_audio'],'pawn_before':list(p.get_actor_location().to_tuple())};s['results'].append(row)
   if abs(d.get_open_angle())<90:s['index']+=1;s.update(phase=1,next=now+.2);return
   p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,80,98/d.get_actor_scale3d().z)),False,True);start=p.get_actor_location();direction=unreal.MathLibrary.get_forward_vector(unreal.Rotator(yaw=d.get_actor_rotation().yaw-90));s.update(phase=6,next=now,until=now+1.2);return
  if s['phase']==6:
   p.add_movement_input(direction,1,False)
   if now<s['until']:return
   p.character_movement.stop_movement_immediately();delta=p.get_actor_location()-start;travel=delta.x*direction.x+delta.y*direction.y;s['results'][-1]['walk_cm']=travel;s['results'][-1]['walk_start']=list(start.to_tuple());s['results'][-1]['walk_end']=list(p.get_actor_location().to_tuple())
   p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,230,102/d.get_actor_scale3d().z)),False,True);d.try_interact();s.update(phase=7,next=now+3);return
  if s['phase']==7:
   s['results'][-1]['closed']=abs(d.get_open_angle())<.1;s['results'][-1]['close_sound']=d.get_editor_property('EventAudio').sound==d.close_sound;assert s['results'][-1]['close_sound'];s['results'][-1]['motion_stopped']=not d.get_editor_property('MotionAudio').is_playing();s['index']+=1;s.update(phase=1,next=now+.2)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
