"""Identical fixed-camera 1440p engine-frame benchmark before and after migration."""
import unreal,time,json,traceback
from pathlib import Path
base=Path(__file__).resolve().parents[1]
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if JOB.get('map'):
 assert JOB['map'] in ['/Game/MaldekRefinement/ForestTest/Forest_Approach_Test','/Game/MaldekRefinement/R12/Station_R12']
 assert levels.load_level(JOB['map'])
editor_world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert editor_world.get_name() in ['Forest_Approach_Test','Station_R12']
assert not levels.is_in_play_in_editor()
performance_settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
previous_throttle=performance_settings.get_editor_property('bThrottleCPUWhenNotForeground')
performance_settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.SystemLibrary.execute_console_command(editor_world,'t.IdleWhenNotForeground 0')
unreal.SystemLibrary.execute_console_command(editor_world,'Slate.bAllowThrottling 0')
out=base/JOB.get('output',('baseline' if editor_world.get_name()=='Forest_Approach_Test' else 'final'));out.mkdir(parents=True,exist_ok=True)
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
shots=[('forest',(-31.7,-46.4,.9),(-26,-37,.9)),('station',(-30,-28,13),(-6,0,4)),('control',(-4,3,5.6),(-4,-3,5.4)),('dock',(4,9,5.6),(0,7,5.4)),('service',(17,-7,2),(5,1,1)),('bridge',(18,28,5.6),(12,9,4.8))]
def wp(p):return unreal.Vector(origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100)
state={'map':editor_world.get_path_name(),'stage':'await_pie','next':time.monotonic(),'i':0,'samples':[],'deadline':time.monotonic()+300,'busy':False,'cameras':shots,'measurement':'Raw engine frames; generated display frames are not counted.','measurement_version':'isolated-editor-v2'}
def finish(world):
 state['editor_rendering_restored']=list(unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False))
 unreal.SystemLibrary.execute_console_command(world,'csvprofile stop')
 unreal.StationMigrationLibrary.set_pie_render_size(0,0)
 performance_settings.set_editor_property('bThrottleCPUWhenNotForeground',previous_throttle)
 state.pop('pawn',None);state['busy']=False
 (out/'performance_capture.json').write_text(json.dumps(state,indent=2))
 levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  now=time.monotonic()
  if now>state['deadline']:raise RuntimeError('Performance capture timed out')
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
  if not pawn or not pc:return
  if state['stage']=='await_pie':
   state['editor_rendering_suppressed']=list(unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True));assert state['editor_rendering_suppressed']
   assert unreal.StationMigrationLibrary.set_pie_render_size(2560,1440)
   state.update(stage='resolution',next=now+4);return
  if now<state['next']:return
  if state['stage']=='resolution':
   state['viewport_size']=list(pc.get_viewport_size());assert state['viewport_size']==[2560,1440],state['viewport_size']
   for cmd in ['r.VSync 0','t.MaxFPS 0','r.GPUStatsEnabled 1','stat none','stat unit','stat RHI','stat streaming','csvprofile start']:
    unreal.SystemLibrary.execute_console_command(world,cmd)
   state['console_settings']={n:unreal.SystemLibrary.get_console_variable_float_value(n) for n in ['r.ScreenPercentage','r.VSync','r.AntiAliasingMethod','sg.ViewDistanceQuality','sg.ShadowQuality','sg.GlobalIlluminationQuality','sg.ReflectionQuality']}
   state['pawn_settings']={'class':pawn.get_class().get_path_name(),'capsule_radius':pawn.capsule_component.get_scaled_capsule_radius(),'capsule_half_height':pawn.capsule_component.get_scaled_capsule_half_height(),'max_step_height':pawn.character_movement.max_step_height,'walkable_floor_angle':pawn.character_movement.get_walkable_floor_angle()}
   state['environment']={}
   for wa in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor):
    if wa.get_actor_label() not in ['Ultra_Dynamic_Weather','Ultra_Dynamic_Sky']:continue
    props={}
    for field in ['Weather','Snow','Rain','Fog','Material Snow Coverage','Wind Intensity','Time Of Day','Begin Play Weather is Random','Random Weather Variation']:
     try:
      value=wa.get_editor_property(field);props[field]=value.get_path_name() if isinstance(value,unreal.Object) else str(value)
     except Exception:pass
    state['environment'][wa.get_actor_label()]=props
   pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   state['pawn']=pawn;state.update(stage='place',next=now+5)
  if state['stage']=='place':
   name,p,q=shots[state['i']];pawn.set_actor_location(wp(p),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)))
   state.update(stage='sample',next=now+8,end=now+20);return
  if state['stage']=='sample':
   sample=dict(unreal.StationMigrationLibrary.capture_pie_frame_stats());sample.update(camera=shots[state['i']][0],slate_delta_ms=dt*1000)
   state['samples'].append(sample)
   if now<state['end']:return
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/(shots[state['i']][0]+'.png')))
   state['i']+=1;state.update(stage='place',next=now+3)
   if state['i']<len(shots):return
   assert all(s.get('width')==2560 and s.get('height')==1440 for s in state['samples'])
   assert any(s.get('gpu_ms',0)>0 for s in state['samples']),'GPU telemetry unavailable'
   assert len({s.get('gpu_ms') for s in state['samples']})>20,'Stale GPU telemetry: stat unit must be active'
   assert len({s.get('frame_ms') for s in state['samples']})>20,'Stale frame telemetry'
   assert len(state['samples'])>600,'Insufficient frames: inspect throttling or severe stalls'
   state['success']=True;finish(world)
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();finish(unreal.EditorLevelLibrary.get_game_world())
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()
