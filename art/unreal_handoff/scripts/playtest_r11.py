import unreal,time,json,traceback,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not levels.is_in_play_in_editor();assert levels.save_current_level();assert levels.load_level('/Game/MaldekRefinement/R11/BlockOut_R11')
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
routes=[('west_dock',[(-2.9,6.3,4),(-2.9,10.5,4)]),('east_dock',[(2.7,7.7,4),(2.7,10.5,4)]),('bridge',[(12,7.9,4),(12,8.6,4),(16,15,4),(19,31.2,4),(19,35.5,4)]),('service',[(7,-3.2,0),(12,-4,0),(17,-9,-.3),(22,-12,-.7),(26,-15,-1),(27.5,-15,-1)]),('workshop',[(31.7,-15.5,-1),(34,-15.5,-1)])]
state={'route':0,'point':1,'stage':'init','next':time.monotonic(),'deadline':time.monotonic()+120,'results':[],'busy':False}
def pos(p):return unreal.Vector(origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100+98)
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  now=time.monotonic();world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  pawn=unreal.GameplayStatics.get_player_pawn(world,0)
  if not pawn:return
  pc=unreal.GameplayStatics.get_player_controller(world,0)
  if now>state['deadline']:raise RuntimeError('Overall route verification timeout')
  if state['stage']=='init':
   light=pawn.get_components_by_class(unreal.SpotLightComponent)[0];state['beam_material']=str(light.get_editor_property('light_function_material'));assert 'M_Flashlight_Optics' in state['beam_material']
   state['wind']=[{'name':a.get_actor_label(),'playing':a.audio_component.is_playing()} for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.AmbientSound)]
   state['cabin_start']=str(next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='R04_12_Gondola').get_actor_transform())
   state['stage']='place'
  if state['stage']=='place':
   name,points=routes[state['route']];pawn.set_actor_location(pos(points[0]),False,True);state.update(stage='settle',next=now+1,point=1,route_start=now);return
  if state['stage']=='settle':
   if now<state['next']:return
   state['stage']='walk';state['waypoint_start']=now
  if state['stage']=='walk':
   name,points=routes[state['route']];target=pos(points[state['point']]);here=pawn.get_actor_location();dx,dy=target.x-here.x,target.y-here.y;dist=math.hypot(dx,dy)
   if abs(here.z-target.z)>60:raise RuntimeError(f'{name}: fell below the path at waypoint {state["point"]}: {here}')
   if now-state['waypoint_start']>12:raise RuntimeError(f'{name}: blocked at waypoint {state["point"]}, distance {dist:.1f}, location {here}')
   if dist>27:
    pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),1,False);return
   state['point']+=1;state['waypoint_start']=now
   if state['point']<len(points):return
   state['results'].append({'route':name,'passed':True,'duration':now-state['route_start']});state['route']+=1
   if state['route']<len(routes):state['stage']='place';return
   state['cabin_end']=str(next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='R04_12_Gondola').get_actor_transform());assert state['cabin_start']==state['cabin_end']
   pawn.set_actor_location(unreal.Vector(-44160,18780,10395),False,True);pc.set_control_rotation(unreal.Rotator(pitch=-4,yaw=-90));state.update(stage='capture',next=now+4);return
  if state['stage']=='capture' and now>state['next']:
   state['success']=True;(out/'play_verification.json').write_text(json.dumps(state,indent=2));unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/'flashlight_on.png'));unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();(out/'play_verification.json').write_text(json.dumps(state,indent=2));unreal.unregister_slate_post_tick_callback(handle)
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play()
