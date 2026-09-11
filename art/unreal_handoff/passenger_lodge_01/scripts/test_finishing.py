"""Exercise twelve lockers with real E input, then walk eighteen combined routes."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'finishing';shots=OUT/'previews/lockers_night';shots.mkdir(exist_ok=True);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
o=json.loads((OUT/'before.json').read_text())['origin'];data=json.loads((OUT/'lockers/exports.json').read_text());specs=[('MIG_PLL_'+r['id'],next(p for p in r['parts'] if p['role']=='Leaf')) for r in data['groups']]
s={'phase':0,'index':JOB.get('start',0),'next':time.monotonic()+12,'deadline':time.monotonic()+700,'checks':{},'images':[],'routes':[],'busy':False}
def advance(n,wait=.2):s.update(phase=n,next=time.monotonic()+wait)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def key(down):unreal.StationMigrationLibrary.send_pie_key('E',down)
def localpoint(v):return unreal.Vector(o[0]-100*(v[0]-24.1),o[1]+100*(4-v[1]),o[2]+499)
def put():
 p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.character_movement.stop_movement_immediately()
 # All fronts face local -Y after FBX conversion. Stand clear of full swings.
 f=d.focus_location;point=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(f.x,-100,f.z));point.z=o[2]+499;p.set_actor_location(point,False,True)
def aim():
 target=unreal.MathLibrary.transform_location(d.pivot.get_world_transform(),d.focus_location);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.GameplayStatics.get_player_camera_manager(p,0).get_camera_location(),target))
def shot(name):
 file=shots/(name+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(file));s['images'].append(str(file))
def finish(error=None):
 key(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(dest/'runtime.json').write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global d,p,pc,label,part,route,target
 if s['busy']:return
 s['busy']=True
 try:
  now=time.monotonic()
  if now<s['next']:return
  assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1600,1000);s['actors']={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet)}
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   if not p.get_components_by_class(unreal.SpotLightComponent)[0].is_visible():p.toggle_flashlight()
   advance(1);return
  if phase==1:
   if s['index']==len(specs):advance(40);return
   label,part=specs[s['index']];d=s['actors'][label];check(label+'_closed_initial',d.get_open_fraction()==0);put();advance(1.5,.3);return
  if phase==1.5:aim();advance(1.6,.3);return
  if phase==1.6:aim();advance(2,.5);return
  if phase==2:
   eye=p.get_actor_location()+unreal.Vector(0,0,64);end=eye+unreal.MathLibrary.get_forward_vector(pc.get_control_rotation())*200;hit=unreal.SystemLibrary.line_trace_single(w,eye,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],unreal.DrawDebugTrace.NONE,True)
   (dest/'focus_probe.json').write_text(json.dumps({'label':label,'eye':str(eye),'target':str(unreal.MathLibrary.transform_location(d.pivot.get_world_transform(),d.focus_location)),'hit':str(hit.to_tuple() if hit else None),'ignored':pc.is_move_input_ignored(),'camera':str(unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location()),'camera_rotation':str(unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_rotation()),'tick':d.is_actor_tick_enabled()},indent=2))
   check(label+'_focus',d.interaction_prompt.is_visible());key(True);advance(3,.15);return
  if phase==3:key(False);check(label+'_cam_releases_first',d.get_cam_release()>0 and (d.get_open_fraction()<.01 or d.get_cam_release()==1));advance(4,1.6);return
  if phase==4:
   s['last_motion']={'label':label,'fraction':d.get_open_fraction(),'obstructed':d.is_obstructed()}
   check(label+'_fully_open',abs(d.get_open_fraction()-1)<.001);check(label+'_not_obstructed',not d.is_obstructed());check(label+'_cam_released',d.get_cam_release()==1);check(label+'_recorded_audio',bool(d.movement_sound) and bool(d.closing_sound));aim();shot(label+'_open');advance(5,1.2);return
  if phase==5:key(True);advance(6,.15);return
  if phase==6:key(False);advance(7,1.5);return
  if phase==7:check(label+'_closed_again',d.get_open_fraction()<.001 and d.get_cam_release()==0);s['index']+=1;advance(1);return
  if phase==40:
   s['actors']={};s['route_data']=list(json.loads((dest/'routes.json').read_text()).items());s['route_index']=0
   p.set_actor_location(localpoint([7,5]),False,True)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet):
    if a.get_actor_label().startswith('MIG_PLL_'):a.try_interact()
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor):
    if a.get_actor_label().startswith(('MIG_PLD_','MIG_PLR_')):a.unlock();a.try_interact()
   advance(41,2);return
  if phase==41:
   if s['route_index']==len(s['route_data']):finish();return
   route=s['route_data'][s['route_index']];p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.character_movement.max_walk_speed=135;p.character_movement.stop_movement_immediately();p.set_actor_location(localpoint(route[1][0]),False,True);s['waypoint']=1;s['walk_started']=now;s['max_floor_error']=0;advance(42,.4);return
  if phase==42:
   target=localpoint(route[1][s['waypoint']]);delta=target-p.get_actor_location();delta.z=0;s['max_floor_error']=max(s['max_floor_error'],abs(p.get_actor_location().z-target.z))
   assert now-s['walk_started']<25,route[0]+' walking timeout'
   if delta.length()<5:
    s['waypoint']+=1
    if s['waypoint']==len(route[1]):
     p.character_movement.stop_movement_immediately();check(route[0]+'_floor',s['max_floor_error']<3);s['routes'].append({'name':route[0],'passed':True,'max_floor_error_cm':s['max_floor_error']});shot(route[0]);advance(43,1.2);return
   else:p.add_movement_input(delta/delta.length(),min(1,max(.12,delta.length()/60)),True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location(),target))
   advance(42,.01);return
  if phase==43:s['route_index']+=1;advance(41);return
 except Exception:
  s.pop('actors',None);finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
