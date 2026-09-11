"""Each kitchen mechanism stops for a player obstruction and retries safely."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'kitchen';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
o=json.loads((OUT/'before.json').read_text())['origin'];s={'phase':0,'index':0,'next':time.monotonic()+12,'deadline':time.monotonic()+180,'checks':{},'stops':{}}
def advance(n,t=.15):s.update(phase=n,next=time.monotonic()+t)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(success=error is None,error=error);(dest/'safety.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global p,actors,d,label
 try:
  if time.monotonic()<s['next']:return
  assert time.monotonic()<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   actors=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet),key=lambda a:a.get_actor_label());check('fifteen_mechanisms',len(actors)==15)
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);advance(1);return
  if phase==1:
   if s['index']==len(actors):finish();return
   d=actors[s['index']];label=d.get_actor_label();f=d.focus_location
   half=unreal.Transform(location=d.open_offset*.5 if d.sliding else unreal.Vector(),rotation=unreal.Rotator(yaw=0 if d.sliding else d.open_angle*.5))
   q=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.MathLibrary.transform_location(half,f));q.z=o[2]+499;p.character_movement.stop_movement_immediately();p.set_actor_location(q,False,True);d.try_interact();advance(2,1.3);return
  if phase==2:
   check(label+'_blocked',d.is_obstructed() and d.get_open_fraction()<.99);s['stops'][label]=d.get_open_fraction();p.set_actor_location(unreal.Vector(o[0]+2200,o[1]-920,o[2]+499),False,True);d.try_interact();advance(3,1.3);return
  if phase==3:check(label+'_retry_open',abs(d.get_open_fraction()-1)<.001);d.try_interact();advance(4,1.3);return
  if phase==4:check(label+'_closed',d.get_open_fraction()<.001 and not d.is_obstructed());s['index']+=1;advance(1);return
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
