"""Neutral/night, front/back, small-angle inspection of normal and inward lock assemblies."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock/previews';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
lamp_editor=aa.spawn_actor_from_class(unreal.RectLight,unreal.Vector(0,0,-10000));lamp_editor.set_actor_label('D04_Transient_KeyLight')
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+180,'files':[]};shots=[]
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(out/'capture.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  s['temporary_light_removed']=aa.destroy_actor(lamp_editor);(out/'capture.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(clean_handle)
 clean_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 global p,pc,lamp,doors
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);pc.set_ignore_move_input(True);pc.set_ignore_look_input(True)
   opening=p.get_component_by_class(unreal.StationOpeningComponent)
   if opening:opening.destroy_component(p)
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)}
   for label in ['R12_Door_Control_side','R12_Door_Quarters','R12_Door_Generator_south']:
    for side in [1,-1]:
     for mode in ['neutral','night']:
      for shift in [-1,0,1]:shots.append((label,side,mode,shift))
   lamp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RectLight) if a.get_actor_label()=='D04_Transient_KeyLight');c=lamp.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(8);c.set_editor_property('source_width',40);c.set_editor_property('source_height',40);c.set_editor_property('attenuation_radius',250);s['phase']=1
  if s['phase']==1:
   if s['index']==len(shots):finish();return
   label,side,mode,shift=shots[s['index']];d=doors[label];t=d.key_lock_root.get_world_transform();target=unreal.MathLibrary.transform_location(t,unreal.Vector(0,side*6,0));pos=unreal.MathLibrary.transform_location(t,unreal.Vector(18+shift*1.5,side*35,14))
   p.set_actor_location(pos-unreal.Vector(0,0,60),False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos,target));d.get_editor_property('KeypadCamera').set_world_location(pos,False,False);d.get_editor_property('KeypadCamera').set_world_rotation(unreal.MathLibrary.find_look_at_rotation(pos,target),False,False);d.get_editor_property('KeypadCamera').set_field_of_view(36);pc.set_view_target_with_blend(d,0)
   d.service_key.set_visibility(side>0);d.service_key.set_relative_location(unreal.Vector(0,12.6,0),False,False)
   for c in p.get_components_by_class(unreal.MeshComponent):c.set_hidden_in_game(True)
   for beam in p.get_components_by_class(unreal.SpotLightComponent):beam.set_visibility(mode=='night')
   lp=unreal.MathLibrary.transform_location(t,unreal.Vector(-15,side*40,30));lamp.set_actor_location(lp,False,True);lamp.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(lp,target),False);lamp.set_actor_hidden_in_game(mode!='neutral')
   s.update(phase=2,next=now+(2 if shift==-1 else .3));return
  if s['phase']==2:
   label,side,mode,shift=shots[s['index']];name=label+('_front_' if side>0 else '_inside_')+mode+'_'+str(shift+1)+'.png';file=out/name;file.unlink(missing_ok=True);unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(file));s.update(phase=3,next=now+.3,awaiting=str(file));return
  if s['phase']==3:
   file=Path(s['awaiting'])
   if not file.exists() or file.stat().st_size<1000:return
   s['files'].append(str(file));s['index']+=1;s.update(phase=1,next=now+.1)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}
