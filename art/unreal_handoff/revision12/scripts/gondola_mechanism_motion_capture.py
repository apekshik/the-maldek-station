"""Local tower inspection, neutral-light and actual night/torch shots in PIE only."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_mechanism'/'motion';out.mkdir(exist_ok=True);plan=json.loads((b/'gondola_route/plan.json').read_text());n=plan['nodes'][1]
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
inspection_light=next((a for a in aa.get_all_level_actors() if a.get_actor_label()=='Gondola_Inspection_Temporary'),None) or aa.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-40,-35,0));inspection_light.set_actor_label('Gondola_Inspection_Temporary');inspection_light.get_components_by_class(unreal.DirectionalLightComponent)[0].set_mobility(unreal.ComponentMobility.MOVABLE);inspection_light.get_components_by_class(unreal.DirectionalLightComponent)[0].set_intensity(0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
shots=[('frame_%02d'%i,[-43489,18579,10789],[-44139,18779,11039],4) for i in range(10)]
s={'phase':'place','i':0,'next':time.monotonic()+15,'busy':False,'images':[],'deadline':time.monotonic()+180}
def finish():
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);(out/'inspection.json').write_text(json.dumps({k:v for k,v in s.items() if k!='light'},indent=2));unreal.unregister_slate_post_tick_callback(handle)
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  aa.destroy_actor(inspection_light);unreal.unregister_slate_post_tick_callback(cleanup_handle)
 cleanup_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline']
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if 'light' not in s:
   next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem)).begin_arrival()
   s['light']=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.DirectionalLight) if a.get_actor_label()=='Gondola_Inspection_Temporary')
  if s['phase']=='place':
   name,eye,target,lux=shots[s['i']];s['light'].get_components_by_class(unreal.DirectionalLightComponent)[0].set_intensity(lux)
   unreal.StationMigrationLibrary.set_pie_render_size(960,600);p.character_movement.stop_movement_immediately();p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True)
   p.set_actor_location(unreal.Vector(*eye)-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*eye),unreal.Vector(*target)));s.update(phase='capture',next=time.monotonic()+.35)
  elif s['phase']=='capture':
   path=out/(shots[s['i']][0]+'.png');unreal.AutomationLibrary.take_high_res_screenshot(960,600,str(path));s['images'].append(str(path));s.setdefault('travel_m',[]).append(next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaMechanism)).rope_travel_meters);s['i']+=1;s.update(phase='place' if s['i']<len(shots) else 'end',next=time.monotonic()+.25)
  else:
   assert all(Path(p).exists() for p in s['images']);s['passed']=True;finish()
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
