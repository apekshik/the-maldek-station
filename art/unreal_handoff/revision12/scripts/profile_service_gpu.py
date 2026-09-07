"""Capture Unreal's own GPU pass breakdown at the paired lower-service camera."""
import unreal,time,json,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
world_name=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name();variant='baseline' if world_name=='Forest_Approach_Test' else 'final'
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
state={'phase':0,'next':0,'busy':False}
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def finish():
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',old)
 ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic();w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if state['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(2560,1440);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
   for cmd in ['r.VSync 0','t.MaxFPS 0','r.GPUStatsEnabled 1','stat none','stat gpu','r.ProfileGPU.ShowUI 0']:unreal.SystemLibrary.execute_console_command(w,cmd)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(wp((17,-7,2)),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp((17,-7,2)),wp((5,1,1))))
   state.update(phase=1,next=now+20)
  elif state['phase']==1:
   unreal.log('R12_GPU_PROFILE_BEGIN_'+variant);unreal.SystemLibrary.execute_console_command(w,'profilegpu');state.update(phase=2,next=now+3)
  elif state['phase']==2:
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(b/variant/'gpu_passes.png'));state.update(phase=3,next=now+4)
  else:unreal.log('R12_GPU_PROFILE_END_'+variant);finish()
 except Exception:unreal.log_error(traceback.format_exc());finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True,'variant':variant}
