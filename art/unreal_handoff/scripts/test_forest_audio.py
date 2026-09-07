"""PIE checks: real route surfaces, five surface fixtures, idle, airborne, and running cadence."""
import unreal,time,json,math,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary
assert not levels.is_in_play_in_editor();assert levels.save_current_level()
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];path=json.loads((out.parent/'revision10/approach_path.json').read_text())['points']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2]+98)
# Transient pads are removed after testing and never saved in the map.
pads=[]
for i,name in enumerate(['Soil','Gravel','Metal','Concrete','Wood']):
 a=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(origin[0]+14000,origin[1]+i*600,origin[2]+5000));a.set_actor_label('TEMP_Audio_'+name);a.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));a.set_actor_scale3d(unreal.Vector(24,4,.2));a.static_mesh_component.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+name));pads.append(a)
cases=[]
for i,name in enumerate(['soil','gravel','metal','concrete','wood']):
 cases.append({'name':name,'surface':i+1,'from':[origin[0]+13000,origin[1]+i*600,origin[2]+5108],'to':[origin[0]+15000,origin[1]+i*600,origin[2]+5108],'speed':350})
cases.append(dict(cases[1],name='gravel_running',speed=600))
def arr(v):return [v.x,v.y,v.z]
cases += [{'name':'actual_forest_path','surface':2,'points':[arr(wp(p)) for p in path[8:33:4]],'speed':350}, {'name':'actual_bridge','surface':3,'points':[arr(wp(p)) for p in [(16,15,4),(17.5,23,4),(19,30,4)]],'speed':350}]
state={'stage':'init','case':0,'busy':False,'results':[],'deadline':time.monotonic()+180}
def audio_test_tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  now=time.monotonic()
  if state['stage']=='cleanup':
   if levels.is_in_play_in_editor():return
   for a in pads:aa.destroy_actor(a)
   levels.save_current_level();unreal.unregister_slate_post_tick_callback(audio_test_handle);return
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0)
  if not pawn:return
  c=pawn.get_components_by_class(unreal.SurfaceFootstepComponent)[0];move=pawn.character_movement
  if now>state['deadline']:raise RuntimeError('Audio test timeout')
  if state['stage']=='init':
   assert len(c.soil_steps)==5 and len(c.metal_steps)==5
   state['ambience']=[{'name':a.get_actor_label(),'playing':a.audio_component.is_playing(),'volume':a.audio_component.volume_multiplier} for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.AmbientSound)]
   pawn.set_actor_location(unreal.Vector(*cases[0]['from']),False,True);state.update(stage='idle_settle',next=now+1);return
  if state['stage']=='idle_settle':
   if now<state['next']:return
   state.update(stage='idle',next=now+2,count=c.footstep_count);return
  if state['stage']=='idle':
   if now<state['next']:return
   assert c.footstep_count==state['count'],'Footsteps while idle';state['results'].append({'name':'idle','passed':True});p=pawn.get_actor_location();p.z+=5000;pawn.set_actor_location(p,False,True);move.set_movement_mode(unreal.MovementMode.MOVE_FALLING);state.update(stage='air',next=now+1,count=c.footstep_count);return
  if state['stage']=='air':
   pawn.add_movement_input(unreal.Vector(1,0,0),1,False)
   if now<state['next']:return
   assert c.footstep_count==state['count'],'Footsteps in air';state['results'].append({'name':'airborne','passed':True});state['stage']='place'
  if state['stage']=='place':
   case=cases[state['case']];points=case.get('points',[case.get('from'),case.get('to')]);state['points']=points;move.stop_movement_immediately();pawn.set_actor_location(unreal.Vector(*points[0]),False,True);pawn.set_editor_property('walk_speed',case['speed']);move.set_movement_mode(unreal.MovementMode.MOVE_WALKING);state.update(stage='settle',next=now+.7,point=1);return
  if state['stage']=='settle':
   if now<state['next']:return
   if cases[state['case']]['name']=='actual_forest_path':unreal.AudioMixerLibrary.start_recording_output(w,20.)
   state.update(stage='walk',count=c.footstep_count,begin=now,surfaces=[],lastcount=c.footstep_count,waypoint=now)
  if state['stage']=='walk':
   case=cases[state['case']];target=unreal.Vector(*state['points'][state['point']]);here=pawn.get_actor_location();dx=target.x-here.x;dy=target.y-here.y;dist=math.hypot(dx,dy)
   if c.footstep_count!=state['lastcount']:state['surfaces'].append({'surface':c.last_surface,'material':c.last_floor_material});state['lastcount']=c.footstep_count
   if now-state['waypoint']>14:raise RuntimeError('Blocked on '+case['name'])
   if dist>35:pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),1,False);return
   state['point']+=1;state['waypoint']=now
   if state['point']<len(state['points']):return
   steps=c.footstep_count-state['count'];assert steps>=3,(case['name'],steps)
   surfaces={v['surface'] for v in state['surfaces']};assert surfaces=={case['surface']},(case['name'],state['surfaces'])
   state['results'].append({'name':case['name'],'passed':True,'steps':steps,'seconds':now-state['begin'],'surfaces':state['surfaces']});state['case']+=1
   if state['case']<len(cases):state['stage']='place';return
   walk=next(r for r in state['results'] if r['name']=='gravel');run=next(r for r in state['results'] if r['name']=='gravel_running');assert run['steps']/run['seconds']>walk['steps']/walk['seconds'],'Running cadence did not increase'
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'footstep_mix',str(out))
   state['success']=True;(out/'audio_validation.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();state['stage']='cleanup'
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();(out/'audio_validation.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();state['stage']='cleanup'
 finally:state['busy']=False
audio_test_handle=unreal.register_slate_post_tick_callback(audio_test_tick);levels.editor_request_begin_play()

