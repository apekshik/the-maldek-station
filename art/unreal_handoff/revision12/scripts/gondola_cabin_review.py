"""Neutral/night/torch review of both sides of the entry, with glancing-angle bursts."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_cabin'/'review';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
light=next((a for a in aa.get_all_level_actors() if a.get_actor_label()=='Cabin_Inspection_Temporary'),None) or aa.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(pitch=-40,yaw=-35));light.set_actor_label('Cabin_Inspection_Temporary');light.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);light.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False);unreal.StationMigrationLibrary.set_editor_rendering_suppressed(True)
views=[('open_night',(170,-520,170),(0,-305,120),0),('open_neutral',(170,-520,170),(0,-305,120),3),('interior_neutral',(0,-255,160),(0,250,115),3),('inside_entry_neutral',(80,-90,165),(0,-315,135),3),('inside_entry_night',(80,-90,165),(0,-315,135),0)]
closed=[('closed_front_neutral',(170,-490,170),(0,-315,135),3),('closed_inside_neutral',(80,-90,165),(0,-315,135),3),('closed_front_night',(170,-490,170),(0,-315,135),0)]
s={'phase':'warm','next':time.monotonic()+25,'deadline':time.monotonic()+180,'index':0,'burst':0,'images':[]}
def finish(error=None):
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();unreal.StationMigrationLibrary.set_editor_rendering_suppressed(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);s.update(passed=error is None,error=error);(out/'report.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle)
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  aa.destroy_actor(light);unreal.unregister_slate_post_tick_callback(cleanup_handle)
 cleanup_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 if time.monotonic()<s['next']:return
 try:
  assert time.monotonic()<s['deadline']
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0);g=next(iter(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.GondolaSystem)));carrier=next(c for c in g.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh');origin=carrier.get_world_location();lamp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.DirectionalLight) if a.get_actor_label()=='Cabin_Inspection_Temporary')
  if s['phase']=='warm':
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True);unreal.StationMigrationLibrary.set_pie_render_size(1440,900);g.begin_arrival();unreal.GameplayStatics.set_global_time_dilation(w,8);s['phase']='arrive'
  elif s['phase']=='arrive':
   if g.door_open_fraction>=.999:g.set_actor_tick_enabled(False);unreal.GameplayStatics.set_global_time_dilation(w,1);s.update(phase='place',next=time.monotonic()+1)
  elif s['phase']=='place':
   entries=closed if s.get('closed') else views;name,eye,target,lux=entries[s['index']];offset=s['burst']*1.5;eye=origin+unreal.Vector(*eye)+unreal.Vector(offset,0,0);p.set_actor_location(eye-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,origin+unreal.Vector(*target)));lamp.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(lux);s.update(phase='capture',next=time.monotonic()+(3 if s['burst']==0 else .15))
   torch=p.get_components_by_class(unreal.SpotLightComponent)[0]
   if torch.is_visible()!=(lux==0):p.toggle_flashlight()
   assert torch.is_visible()==(lux==0),'Torch toggle was blocked'
  elif s['phase']=='capture':
   entries=closed if s.get('closed') else views;name=entries[s['index']][0];path=out/(name+'_%02d.png'%s['burst']);path.unlink(missing_ok=True);unreal.AutomationLibrary.take_high_res_screenshot(1440,900,str(path));s['images'].append(str(path));s.update(phase='image_wait',next=time.monotonic()+.2)
  elif s['phase']=='image_wait':
   if not Path(s['images'][-1]).exists():return
   s['burst']+=1
   if s['burst']>=3:s['index']+=1;s['burst']=0
   entries=closed if s.get('closed') else views
   if s['index']<len(entries):s['phase']='place'
   elif not s.get('closed'):
    p.set_actor_location(origin+unreal.Vector(0,-150,105),False,True);g.set_actor_tick_enabled(True);g.send_gondola();s['phase']='closing'
   else:finish();return
  elif s['phase']=='closing':
   if g.door_open_fraction<=0:g.set_actor_tick_enabled(False);s.update(closed=True,index=0,phase='place')
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
