"""Actual PIE night/flashlight views; small camera shifts expose reveal artifacts."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'previews/surfaces_night';dest.mkdir(exist_ok=True);o=json.loads((OUT/'before.json').read_text())['origin']
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
views=[('outside',[-21,5.4,5.65],[-20.8,4,5.65]),('inside',[-21,2.7,5.65],[-20.8,4,5.65]),('hall',[-22,-5,5.65],[-16,2,5.4])]
s={'phase':'warm','next':time.monotonic()+12,'deadline':time.monotonic()+150,'index':0,'burst':0,'images':[],'busy':False}
def finish(error=None):
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (OUT/'surface_night_review.json').write_text(json.dumps({'error':error,'images':s['images'],'mode':'PIE; existing game night lighting and player flashlight; 2cm glancing camera shifts'},indent=2))
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline']
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if s['phase']=='warm':
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);unreal.StationMigrationLibrary.set_pie_render_size(1600,1000)
   torch=p.get_components_by_class(unreal.SpotLightComponent)[0]
   if not torch.is_visible():p.toggle_flashlight()
   s['phase']='place'
  if s['index']==len(views):finish();return
  name,eye,target=views[s['index']];eye=wp(eye)+unreal.Vector(s['burst']*2,0,0)
  if s['phase']=='place':
   p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,wp(target)));s.update(phase='capture',next=time.monotonic()+(4 if s['burst']==0 else .3))
  elif s['phase']=='capture':
   path=dest/(name+'_%02d.png'%s['burst']);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path));s['pending']=str(path);s.update(phase='wait',next=time.monotonic()+1)
  else:
   if not Path(s['pending']).exists():return
   s['images'].append(s['pending']);s['burst']+=1
   if s['burst']==3:s['index']+=1;s['burst']=0
   s['phase']='place'
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
