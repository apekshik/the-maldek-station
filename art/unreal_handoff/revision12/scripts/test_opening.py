"""Exercise opening timing, input gates, switch audio and focus through the real pawn."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'opening';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
mode=JOB.get('mode','interactive');state={'mode':mode,'checks':[],'flags':set(),'deadline':time.monotonic()+100}
def widgets(w):return unreal.WidgetLibrary.get_all_widgets_of_class(w,unreal.StationOpeningWidget,True)
def check(name,condition):
 assert condition,name
 state['checks'].append(name)
def tick(dt):
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  c=p.get_components_by_class(unreal.StationOpeningComponent)[0];pc=unreal.GameplayStatics.get_player_controller(w,0)
  light=p.get_components_by_class(unreal.SpotLightComponent)[0];focus=p.get_components_by_class(unreal.StationPlayerPresentationComponent)[0]
  t=c.elapsed
  if time.monotonic()>state['deadline']:raise RuntimeError('Opening test timeout')
  if 'recording' not in state['flags']:
   steps=p.get_components_by_class(unreal.SurfaceFootstepComponent)[0]
   check('recorded footsteps preserved',len(steps.soil_steps)==18 and len(steps.metal_steps)==15)
   unreal.AudioMixerLibrary.start_recording_output(w,35);state['flags'].add('recording')
  if t>=2 and 'title' not in state['flags']:
   check('title widget exists',len(widgets(w))==1);check('title holds movement',pc.is_move_input_ignored());check('title holds look',pc.is_look_input_ignored())
   before=light.is_visible();target=focus.get_target_focus();p.toggle_flashlight();p.focus_flashlight_in()
   check('flashlight gated during title',light.is_visible()==before and c.switch_count==0);check('scroll gated during title',focus.get_target_focus()==target)
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/f'{mode}_title.png')+'"');state['flags'].add('title')
  if t>=7.5 and 'hints' not in state['flags']:
   check('movement restored',not pc.is_move_input_ignored());check('look restored',not pc.is_look_input_ignored());check('hints remain visible',len(widgets(w))==1)
   unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename="'+str(out/f'{mode}_hints.png')+'"');state['flags'].add('hints')
  if mode=='interactive':
   if t>=8.5 and 'off' not in state['flags']:
    before=light.is_visible();p.toggle_flashlight();check('F changes light and plays one click',light.is_visible()!=before and c.switch_count==1);state['flags'].add('off')
   if t>=9.3 and 'on' not in state['flags']:
    p.toggle_flashlight();check('second F plays second click',c.switch_count==2);check('toggle acknowledged',c.tried_toggle);state['flags'].add('on')
   if t>=10 and 'focus' not in state['flags']:
    before=focus.get_target_focus();p.focus_flashlight_in();check('scroll up narrows beam',focus.get_target_focus()>before);p.focus_flashlight_out();check('scroll down restores width',abs(focus.get_target_focus()-before)<.001);check('scroll acknowledged',c.tried_focus);check('scroll does not click switch',c.switch_count==2);state['flags'].add('focus')
   end=15
  else:end=29
  if t>=end:
   check('onboarding removed',len(widgets(w))==0);check('no lingering input lock',not pc.is_move_input_ignored() and not pc.is_look_input_ignored())
   if mode!='interactive':check('no unsolicited switch clicks',c.switch_count==0)
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,mode+'_mix',str(out))
   report={'success':True,'mode':mode,'checks':state['checks'],'elapsed':t,'switch_count':c.switch_count}
   (out/f'{mode}_validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
 except Exception:
  (out/f'{mode}_validation.json').write_text(json.dumps({'success':False,'checks':state['checks'],'error':traceback.format_exc()},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play()
RESULT={'started':True,'mode':mode}
