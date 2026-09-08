"""Matched in-game views using the user's existing lighting without overrides."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'fog_density'/'views';out.mkdir(parents=True,exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
shots=JOB.get('shots') or [['rear',(-10,-12,5.7),(-17,-31,0)],['approach',(-13,-17,5.7),(-31,-45,-1)],['front',(-7,6,5.8),(-7,34,-12)],['side',(16,-10,5.7),(30,-29,0)]]
if isinstance(shots[0],str):shots=[shots]
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':'place','index':0,'next':time.monotonic()+JOB.get('warmup',35),'deadline':time.monotonic()+240,'images':[],'busy':False}
def end():
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);(out/'capture.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'],'Capture timed out'
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  sky=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) if a.get_actor_label()=='Ultra_Dynamic_Sky')
  expected=json.loads((b/'fog_density'/'settings.json').read_text())['after']['Scale Fog Density']
  actual=sky.get_editor_property('Scale Fog Density');assert abs(actual-expected)<.001
  s['runtime_density_scale']=actual
  if s['phase']=='place':
   unreal.StationMigrationLibrary.set_pie_render_size(1800,1000);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);p.character_movement.stop_movement_immediately();p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
   name,a,q=shots[s['index']];p.set_actor_location(wp(a),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(a),wp(q)))
   s.update(phase='capture',next=time.monotonic()+7)
  elif s['phase']=='capture':
   name=shots[s['index']][0];path=out/(name+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1800,1000,str(path));s['images'].append(str(path));s['index']+=1;s.update(phase='place' if s['index']<len(shots) else 'end',next=time.monotonic()+2)
  else:s['success']=True;end()
 except Exception:s['error']=traceback.format_exc();end()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True,'stage':str(out)}
