"""Walk the actual character up/down both stairs in the isolated PIE map."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin'];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
up=[[-7.2,-15.5,0],[-7.2,-6.6,4],[-5,-6.6,4]]
arrival=[[-15.51,-16.35,0],[-23.1,-16.35,4],[-23.5,-16,4],[-23.5,-14.3,4]]
tests=[('bypass_up',up),('bypass_down',list(reversed(up))),('arrival_up',arrival),('arrival_down',list(reversed(arrival)))]
surface=globals().get('JOB',{}).get('surface',False)
if surface:
 exit_path=[[-17.1,2.5,4],[-17.1,5.5,4]]
 tests=[('public_exit_out',exit_path),('public_exit_in',list(reversed(exit_path)))]
state={'phase':'warm','next':time.monotonic()+12,'deadline':time.monotonic()+200,'index':0,'results':[],'samples':[],'busy':False}
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def end(error=None):
 state.update(passed=error is None and len(state['results'])==len(tests),error=error,phase='finished')
 (OUT/('surface_playtest.json' if surface else 'playtest.json')).write_text(json.dumps({k:v for k,v in state.items() if k!='busy'},indent=2))
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  now=time.monotonic();assert now<state['deadline'],'PIE deadline'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not pawn or now<state['next']:return
  if state['phase']=='warm':
   state['capsule']={'radius':pawn.capsule_component.get_scaled_capsule_radius(),'half_height':pawn.capsule_component.get_scaled_capsule_half_height()};state['phase']='place'
  name,points=tests[state['index']]
  if state['phase']=='place':
   pawn.character_movement.stop_movement_immediately();pawn.character_movement.max_walk_speed=180;pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);pc.set_ignore_move_input(False)
   pawn.set_actor_location(wp(points[0])+unreal.Vector(0,0,state['capsule']['half_height']+8),False,True);state.update(phase='walk',next=now+2,started=now+2,point=1);return
  loc=pawn.get_actor_location();target=wp(points[state['point']]);delta=target-loc;delta.z=0;distance=delta.length()
  state['samples'].append({'test':name,'time':now-state['started'],'point':state['point'],'distance_cm':distance,'foot_source_z':(loc.z-o[2]-state['capsule']['half_height'])/100})
  assert now-state['started']<32,f'{name} stalled at point {state["point"]}, {distance:.1f} cm remaining'
  if distance<12:
   expected=points[state['point']][2];foot=(loc.z-o[2]-state['capsule']['half_height'])/100;assert abs(foot-expected)<.35,(name,'wrong floor height',foot,expected)
   pawn.character_movement.stop_movement_immediately();state['point']+=1
   if state['point']==len(points):
    state['results'].append({'name':name,'passed':True,'duration':now-state['started']});state['index']+=1
    if state['index']==len(tests):end();return
    state.update(phase='place',next=now+1)
  else:pawn.add_movement_input(delta/distance,min(1,max(.15,distance/80)),True)
 except Exception:end(traceback.format_exc())
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
