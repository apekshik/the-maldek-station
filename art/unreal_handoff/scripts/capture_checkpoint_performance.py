"""Capture fixed cameras in an actual 1440p PIE window; fail on wrong resolution."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[2]/'checkpoints/pre_vf07'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
origin=json.loads((out.parents[1]/'unreal_handoff/working_level_report.json').read_text())['station_origin']
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
for n,v in [('NewWindowWidth',2560),('NewWindowHeight',1440)]:settings.set_editor_property(n,v)
shots=[('forest',(-31.7,-46.4,.9),(-26,-37,.9)),('station',(-30,-28,13),(-6,0,4)),('control',(-4,3,5.6),(-4,-3,5.4)),('dock',(4,9,5.6),(0,7,5.4)),('service',(17,-7,2),(5,1,1)),('bridge',(18,28,5.6),(12,9,4.8))]
def wp(p):return unreal.Vector(origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100)
state={'stage':'await_pie','next':time.monotonic(),'i':0,'samples':[],'deadline':time.monotonic()+600,'busy':False}
stats=['STAT_FrameTime','STAT_GameThreadTime','STAT_RenderThreadTime','STAT_GPUFrameTime','STAT_RHIDrawPrimitiveCalls','STAT_TexturePoolAllocatedSize','STAT_TotalGPUAllocatedMemory']
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
   unreal.SystemLibrary.execute_console_command(world,'r.FullScreenMode 1',pc); unreal.SystemLibrary.execute_console_command(world,'fullscreen',pc)
   state.update(stage='resolution',next=now+90);return
  if state['stage']=='resolution' and now<state['next']:return
  if state['stage']=='resolution':
   state['viewport_size']=list(pc.get_viewport_size())
   if state['viewport_size']!=[2560,1440]:raise RuntimeError('Require actual 2560x1440 viewport: '+str(state['viewport_size']))
   for cmd in ['r.VSync 0','t.MaxFPS 0','stat unit','stat RHI','stat streaming','csvprofile start']:
    unreal.SystemLibrary.execute_console_command(world,cmd)
   state['console_settings']={n:unreal.SystemLibrary.get_console_variable_float_value(n) for n in ['r.ScreenPercentage','r.VSync','r.AntiAliasingMethod','sg.ViewDistanceQuality','sg.ShadowQuality','sg.GlobalIlluminationQuality','sg.ReflectionQuality']}
   state['pawn']={'class':pawn.get_class().get_path_name(),'capsule_radius':pawn.capsule_component.get_scaled_capsule_radius(),'capsule_half_height':pawn.capsule_component.get_scaled_capsule_half_height(),'max_step_height':pawn.character_movement.max_step_height,'walkable_floor_angle':pawn.character_movement.get_walkable_floor_angle()}
   state['camera']=pawn; pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   pc.set_view_target_with_blend(state['camera'],0)
   state.update(stage='place',next=now+5)
  if now<state['next']:return
  if state['stage']=='place':
   name,p,q=shots[state['i']];cam=state['camera'];cam.set_actor_location(wp(p),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)))
   state.update(stage='sample',next=now+8,end=now+20);return
  if state['stage']=='sample':
   state['samples'].append({'camera':shots[state['i']][0],'delta_ms':dt*1000,'stats':{n:unreal.AutomationLibrary.get_stat_inc_average(n) for n in stats}})
   if now<state['end']:return
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/('baseline_'+shots[state['i']][0]+'.png')))
   state['i']+=1;state.update(stage='place',next=now+3)
   if state['i']<len(shots):return
   state['success']=True
   unreal.SystemLibrary.execute_console_command(world,'csvprofile stop')
   state.pop('camera');(out/'performance_capture.json').write_text(json.dumps(state,indent=2))
   levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  state['success']=False;state['error']=traceback.format_exc();state.pop('camera',None)
  (out/'performance_capture.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)





