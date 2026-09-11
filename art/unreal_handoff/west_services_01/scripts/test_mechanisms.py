import unreal,time,json,traceback
from pathlib import Path
P=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'next':time.monotonic()+10,'index':0,'results':[],'deadline':time.monotonic()+240,'busy':False}
def finish(error=None):
 s.update(error=error,passed=error is None and all(r['open'] and r['closed'] for r in s['results']));(P/'mechanism_runtime.json').write_text(json.dumps({k:v for k,v in s.items() if k not in ['busy','actors']},indent=2));unreal.unregister_slate_post_tick_callback(handle);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);ls.editor_request_end_play()
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  now=time.monotonic();assert now<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  if s['phase']==0:
   s['actors']={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet) if a.get_actor_label().startswith('MIG_WS_')};s['names']=sorted(n for n in s['actors'] if not JOB.get('only') or n in JOB['only']);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(p.get_actor_location()+unreal.Vector(0,0,3000),False,True);s['phase']=1
  if s['index']==len(s['names']):finish();return
  name=s['names'][s['index']];a=s['actors'][name]
  if s['phase']==1:
   # Open the wire door before testing its trays.
   if 'Secure_tray' in name:
    door=s['actors']['MIG_WS_WSP_Secure_door_hinge']
    if door.is_obstructed():
     s['results'].append({'name':name,'open':False,'closed':False,'issue':'wire door blocked'});s.update(index=s['index']+1,phase=1,next=now+.1);return
    if door.get_open_fraction()<.99:door.try_interact();s.update(next=now+1.8);return
   a.try_interact();s.update(phase=2,next=now+2)
  elif s['phase']==2:
   s['current']={'name':name,'open':a.get_open_fraction()>.999,'fraction':a.get_open_fraction(),'obstructed':a.is_obstructed()}
   if a.is_obstructed():s['current']['closed']=False;s['results'].append(s.pop('current'));s.update(index=s['index']+1,phase=1,next=now+.1);return
   a.try_interact();s.update(phase=3,next=now+2)
  elif s['phase']==3:
   s['current']['closed_fraction']=a.get_open_fraction();s['current']['closed_obstructed']=a.is_obstructed();s['current']['closed']=a.get_open_fraction()<.001;s['results'].append(s.pop('current'));s.update(index=s['index']+1,phase=1,next=now+.1)
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
