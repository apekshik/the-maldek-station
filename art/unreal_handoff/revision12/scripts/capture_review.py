"""Fixed defect views in production PIE and temporary neutral inspection lighting."""
import unreal,json,time,traceback
from pathlib import Path
base=Path(__file__).resolve().parents[1];out=base/'reviews'/JOB.get('stage','full');out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not levels.is_in_play_in_editor()
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
shots=JOB.get('shots') or [
 ['doorway',(-2.5,2.5,5.6),(-3.3,-.4,4.9)],['front_grating',(-5,4.2,6),(-5,.4,4)],
 ['rear_cleanup',(23,-10,10),(13,-2,0)],['sideways_arrival',(-25,-22,9),(-17,-14,3)],
 ['quarters_stair',(5,-13,9),(-.6,-6.8,6)],['dock_border',(5,12,8),(4,5.5,4)],
 ['quarters_interior',(-2.5,-3.8,9.2),(-6,-.8,8.5)],['lower_floor',(10,-3,2),(3,4,1)],
 ['water_terrace',(26,-13,7),(21,-18,2)],['whole_station',(-28,23,22),(-3,-3,4)]]
lamp=aa.spawn_actor_from_class(unreal.RectLight,wp((0,0,30)),unreal.Rotator(pitch=-60))
lamp.set_actor_label('R12_Transient_Review_Lamp');lamp.set_actor_hidden_in_game(True)
lc=lamp.get_component_by_class(unreal.RectLightComponent);lc.set_mobility(unreal.ComponentMobility.MOVABLE);lc.set_intensity(15000);lc.set_editor_property('attenuation_radius',16000);lc.set_editor_property('source_width',2000);lc.set_editor_property('source_height',1500)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
state={'phase':'start','next':time.monotonic()+8,'index':0,'mode':'night','images':[],'busy':False,'deadline':time.monotonic()+600}
def end():
 unreal.StationMigrationLibrary.set_pie_render_size(0,0);levels.editor_request_end_play();state.update(phase='cleanup',next=time.monotonic()+2)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic()
  if state['phase']=='cleanup':
   if levels.is_in_play_in_editor():return
   assert aa.destroy_actor(lamp);assert levels.save_current_level();settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
   state.update(success='error' not in state,inspection_lights_removed=True);(out/'capture.json').write_text(json.dumps(state,indent=2));unreal.unregister_slate_post_tick_callback(handle);return
  assert now<state['deadline'],'Review capture timeout'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not pawn or not pc:return
  if state['phase']=='start':
   unreal.StationMigrationLibrary.set_pie_render_size(2560,1440);pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   unreal.SystemLibrary.execute_console_command(w,'stat none');state['phase']='place'
  if state['phase']=='place':
   name,p,q=shots[state['index']];pos=wp(p);pawn.set_actor_location(pos,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos,wp(q)))
   if state['mode']=='inspection':
    light=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RectLight) if a.get_actor_label()=='R12_Transient_Review_Lamp')
    lp=pos+unreal.Vector(0,0,500);light.set_actor_location(lp,False,True);light.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(lp,wp(q)),False)
   state.update(phase='capture',next=now+9);return
  if state['phase']=='capture':
   name=shots[state['index']][0];file=out/(name+'_'+state['mode']+'.png');unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(file));state['images'].append(str(file));state['index']+=1
   if state['index']<len(shots):state.update(phase='place',next=now+2);return
   state.update(phase='finish_wait' if state['mode']=='inspection' else 'switch_mode',next=now+3);return
  if state['phase']=='finish_wait':end();return
  if state['phase']=='switch_mode':
   light=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RectLight) if a.get_actor_label()=='R12_Transient_Review_Lamp');light.set_actor_hidden_in_game(False)
   for camera in pawn.get_components_by_class(unreal.CameraComponent):
    pp=camera.get_editor_property('post_process_settings');pp.set_editor_property('override_auto_exposure_bias',True);pp.set_editor_property('auto_exposure_bias',-3);camera.set_editor_property('post_process_settings',pp);camera.set_editor_property('post_process_blend_weight',1)
   for beam in pawn.get_components_by_class(unreal.SpotLightComponent):beam.set_visibility(False)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    if a.get_actor_label()=='Ultra_Dynamic_Weather':
     for nc in a.get_components_by_class(unreal.NiagaraComponent):nc.deactivate()
    for mc in a.get_components_by_class(unreal.StaticMeshComponent):
     if not mc.static_mesh or not mc.static_mesh.get_path_name().startswith('/Game/MaldekRefinement/R12/Meshes/'):continue
     for i,s in enumerate(mc.static_mesh.static_materials):
      if 'glass' in str(s.material_slot_name).lower():continue
      path='/Game/MaldekRefinement/R12/Materials/Instances/MI_Dry_'+str(s.material_slot_name)
      if unreal.EditorAssetLibrary.does_asset_exist(path):mc.set_material(i,unreal.load_asset(path))
   state.update(mode='inspection',index=0,phase='place',next=now+3)
 except Exception:state['error']=traceback.format_exc();end()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play();RESULT={'started':True,'shots':len(shots)}
