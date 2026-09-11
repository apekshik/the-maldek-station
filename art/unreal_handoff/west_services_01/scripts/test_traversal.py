"""Walk the actual character up/down both stairs in the isolated PIE map."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'baseline.json').read_text())['origin'];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
import sys
sys.path.insert(0,str(OUT/'scripts'))
from routes import paths
tests=[(n,p) for n,p in paths.items()]+[(n+'_reverse',list(reversed(p))) for n,p in paths.items() if n in ['North_steps_to_rescue','Lower_service','Ramp_to_parcels']]
state={'phase':'warm','next':time.monotonic()+12,'deadline':time.monotonic()+1000,'index':0,'results':[],'samples':[],'busy':False}
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def end(error=None):
 state.update(passed=error is None and len(state['results'])==len(tests),error=error,phase='finished')
 (OUT/'traversal_runtime.json').write_text(json.dumps({k:v for k,v in state.items() if k!='busy'},indent=2))
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
   state['capsule']={'radius':pawn.capsule_component.get_scaled_capsule_radius(),'half_height':pawn.capsule_component.get_scaled_capsule_half_height()};state['phase']='doors'
   for c in pawn.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(pawn)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet):
    if a.get_actor_label().startswith('MIG_WS_') and any(n in a.get_actor_label() for n in ['WSP_Door_hinge','WSR_Door_','WSE_Door_hinge']):a.try_interact()
   state['next']=now+3;return
  if state['phase']=='doors':state['phase']='place'
  name,points=tests[state['index']]
  if state['phase']=='place':
   pawn.character_movement.stop_movement_immediately();pawn.character_movement.max_walk_speed=180;pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);pc.set_ignore_move_input(False)
   pawn.set_actor_location(wp(points[0])+unreal.Vector(0,0,state['capsule']['half_height']+8),False,True);state.update(phase='walk',next=now+2,started=now+2,point=1);return
  loc=pawn.get_actor_location();target=wp(points[state['point']]);delta=target-loc;delta.z=0;distance=delta.length()
  state['samples'].append({'test':name,'time':now-state['started'],'point':state['point'],'distance_cm':distance,'foot_source_z':(loc.z-o[2]-state['capsule']['half_height'])/100})
  assert now-state['started']<110,f'{name} stalled at point {state["point"]}, {distance:.1f} cm remaining'
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
