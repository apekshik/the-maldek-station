"""Drive the inherited player through surveyed routes in PIE using ordinary movement input."""
import unreal,json,time,math,traceback,re
from pathlib import Path
base=Path(__file__).resolve().parents[1];repo=base.parents[2]
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
assert not levels.is_in_play_in_editor()
layout=json.loads((repo/'art/blender/visual_fidelity_07/layout.json').read_text())
routes=layout['routes']
if JOB.get('extra_routes'):
 routes=routes+JOB['extra_routes']
if JOB.get('names'):routes=[r for r in routes if r['name'] in JOB['names']]
elif JOB.get('stage')=='Circulation':
 routes=[r for r in routes if r['name'] not in ['Completed rear hall approach','Quarters landing and doorway','Control front approach','Boarding threshold']]
tests=[{'name':r['name'],'direction':d,'points':r['points'][::1 if d=='forward' else -1]} for r in routes for d in ['forward','reverse']]
assert tests
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100)
def local(v):return [(origin[0]-v.x)/100,(v.y-origin[1])/100,(v.z-origin[2])/100]
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
state={'phase':'await','index':0,'results':[],'busy':False,'deadline':time.monotonic()+1800,'scope':JOB.get('stage','Full'),'teleport_policy':'Only between independent tests; no teleport, flying, jumping or crouching during a route.'}
out=base/JOB.get('report','routes_'+JOB.get('stage','full').lower()+'.json')
def save():out.write_text(json.dumps({k:v for k,v in state.items() if k!='busy'},indent=2))
def gondola_snapshot():
 w=unreal.EditorLevelLibrary.get_game_world()
 if not w:return {}
 names={'R04_12_Gondola'}|{r['name'].replace('SM_','') for r in json.loads((base/'handoff_manifest.json').read_text())['chunks'] if r['collection'] in ['12_Gondola','VF06_Gondola_Details']}
 return {a.get_actor_label():re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',str(a.get_actor_transform())) for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) if a.get_actor_label() in names}
def finish():
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 state['gondola_end']=gondola_snapshot();state['gondola_stationary']=state.get('gondola_start')==state['gondola_end']
 state['success']=len(state['results'])==len(tests) and all(r['passed'] for r in state['results'])
 state['phase']='finished';save();levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def result(pawn,passed,reason):
 row=state['current'];row.update(passed=passed,reason=reason,end=local(pawn.get_actor_location()),elapsed_seconds=time.monotonic()-state['started'])
 if not passed:
  q=wp(tests[state['index']]['points'][min(state['point'],len(tests[state['index']]['points'])-1)])
  p=pawn.get_actor_location();q.z=p.z
  hit=unreal.SystemLibrary.capsule_trace_single(pawn,p,q,34,94,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[pawn],unreal.DrawDebugTrace.NONE,True)
  row['blocking_trace']=[str(v) for v in hit.to_tuple()]
 state['results'].append(row);state['index']+=1;state['phase']='place';save()
 if state['index']==len(tests):finish()
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  now=time.monotonic();assert now<state['deadline'],'Route suite deadline'
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
  if not pawn or not pc:return
  move=pawn.character_movement;half=pawn.capsule_component.get_scaled_capsule_half_height()
  if state['phase']=='await':
   state['gondola_start']=gondola_snapshot()
   state['player']={'class':pawn.get_class().get_path_name(),'radius_cm':pawn.capsule_component.get_scaled_capsule_radius(),'half_height_cm':half,'max_step_cm':move.max_step_height,'slope_degrees':move.get_walkable_floor_angle(),'max_walk_speed':move.max_walk_speed}
   state.update(phase='warm',next=now+8);return
  if state['phase']=='warm':
   if now<state['next']:return
   state['phase']='place'
  if state['phase']=='place':
   test=tests[state['index']];p=wp(test['points'][0]);p.z+=half+8
   move.stop_movement_immediately();pawn.set_actor_location(p,False,True);move.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
   state.update(phase='settle',next=now+1,point=1,started=now,last_progress=now,best=1e20,last_sample=0)
   foot=pawn.get_component_by_class(unreal.SurfaceFootstepComponent)
   state['current']={'name':test['name'],'direction':test['direction'],'passed':False,'samples':[],'max_height_error_cm':0,'max_airborne_seconds':0,'initial_footstep_count':foot.footstep_count if foot else None}
   state['air_start']=None;return
  if state['phase']=='settle':
   if now<state['next']:return
   state['phase']='walk';state['last_progress']=now
  if state['phase']=='walk':
   points=tests[state['index']]['points'];p=pawn.get_actor_location();target=wp(points[state['point']]);dx=target.x-p.x;dy=target.y-p.y;distance=math.hypot(dx,dy)
   feet=p.z-half;previous=wp(points[state['point']-1]);segx=target.x-previous.x;segy=target.y-previous.y
   t=max(0,min(1,((p.x-previous.x)*segx+(p.y-previous.y)*segy)/max(1,segx*segx+segy*segy)))
   expected=previous.z+(target.z-previous.z)*t;height_error=abs(feet-expected)
   row=state['current'];row['max_height_error_cm']=max(row['max_height_error_cm'],height_error)
   if move.is_falling():
    if state['air_start'] is None:state['air_start']=now
    row['max_airborne_seconds']=max(row['max_airborne_seconds'],now-state['air_start'])
   else:state['air_start']=None
   if now-state['last_sample']>.15:
    foot=pawn.get_component_by_class(unreal.SurfaceFootstepComponent)
    row['samples'].append({'p':local(p),'feet_z':(feet-origin[2])/100,'point':state['point'],'falling':move.is_falling(),'footstep_count':foot.footstep_count if foot else None,'surface':foot.last_surface if foot else None});state['last_sample']=now
   if height_error>65:result(pawn,False,'Floor elevation deviates more than 65 cm');return
   if row['max_airborne_seconds']>.6:result(pawn,False,'Unsupported ordinary route');return
   if distance<12:
    state['point']+=1;state['best']=1e20;state['last_progress']=now
    if state['point']==len(points):move.stop_movement_immediately();result(pawn,True,'Reached all waypoints using walking input');return
    target=wp(points[state['point']]);dx=target.x-p.x;dy=target.y-p.y;distance=math.hypot(dx,dy)
   if distance<state['best']-2:state['best']=distance;state['last_progress']=now
   if now-state['last_progress']>3:result(pawn,False,'No progress for 3 seconds');return
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p,unreal.Vector(target.x,target.y,p.z)))
   pawn.add_movement_input(unreal.Vector(dx/max(distance,1),dy/max(distance,1),0),min(1,max(.15,distance/80)),False)
 except Exception:
  state['error']=traceback.format_exc();finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play();RESULT={'started':True,'tests':len(tests),'report':str(out)}
