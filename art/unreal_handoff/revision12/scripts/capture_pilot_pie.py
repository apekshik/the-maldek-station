import unreal,time,json,traceback
from pathlib import Path
base=Path(__file__).resolve().parents[1];out=base/'pilot'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not levels.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for old_lamp in aa.get_all_level_actors():
 if isinstance(old_lamp,unreal.RectLight) and old_lamp.get_actor_label()=='R12_Transient_Pilot_Lamp':aa.destroy_actor(old_lamp)
del old_lamp
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
rows=json.loads((base/'probe_import.json').read_text())['assets']
baked=json.loads((base/'baked_materials.json').read_text());pm=json.loads((base/'probe_manifest.json').read_text())
for name,info in pm['materials'].items():
 mi=unreal.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_'+info['slot']);entry=baked['sets'][baked['materials'][name]['set']]
 values=[unreal.TextureParameterValue(parameter_info=unreal.MaterialParameterInfo(name=ch),parameter_value=unreal.load_asset('/Game/MaldekRefinement/R12/Textures/'+Path(file).stem)) for ch,file in entry['textures'].items()]
 mi.set_editor_property('texture_parameter_values',values);unreal.MaterialEditingLibrary.update_material_instance(mi);unreal.EditorAssetLibrary.save_loaded_asset(mi)
for row in rows:
 a=next(a for a in aa.get_all_level_actors() if a.get_path_name()==row['actor']);p=row['inspection_location_m'];a.set_actor_location(wp((p[0],p[1],p[2]+30)),False,True)
levels.save_current_level()
lamp=aa.spawn_actor_from_class(unreal.RectLight,wp((-30,1,46)),unreal.MathLibrary.find_look_at_rotation(wp((-30,1,46)),wp((-30,-4,43))))
lamp.set_actor_label('R12_Transient_Pilot_Lamp');lamp.set_actor_hidden_in_game(True)
c=lamp.get_component_by_class(unreal.RectLightComponent);c.set_intensity(100);c.set_editor_property('attenuation_radius',1800);c.set_editor_property('source_width',600);c.set_editor_property('source_height',400)
state={'stage':0,'next':time.monotonic()+6,'deadline':time.monotonic()+100}
def tick(dt):
 if time.monotonic()<state['next']:return
 if state['stage']==5:
  if levels.is_in_play_in_editor():return
  assert aa.destroy_actor(lamp)
  assert levels.save_current_level()
  (out/'capture.json').write_text(json.dumps({'success':'error' not in state,'error':state.get('error'),'night':'night.png','inspection':'inspection.png','inspection_method':'temporary neutral rect light and dry material/weather overrides in PIE; production weather retained','inspection_lights_removed':True},indent=2))
  unreal.unregister_slate_post_tick_callback(handle);return
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  pawn=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not pawn or not pc:return
  if time.monotonic()>state['deadline']:raise RuntimeError('Pilot capture timeout')
  if state['stage']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(2560,1440);pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   pawn.set_actor_location(wp((-32,2,45)),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp((-32,2,45)),wp((-30,-4,43))))
   unreal.SystemLibrary.execute_console_command(w,'stat none');state.update(stage=1,next=time.monotonic()+15);return
  if state['stage']==1:
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/'night.png'));state.update(stage=2,next=time.monotonic()+4);return
  if state['stage']==2:
   light=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RectLight) if a.get_actor_label()=='R12_Transient_Pilot_Lamp')
   light.set_actor_hidden_in_game(False)
   for pcamera in pawn.get_components_by_class(unreal.CameraComponent):
    settings=pcamera.get_editor_property('post_process_settings')
    settings.set_editor_property('override_auto_exposure_bias',True);settings.set_editor_property('auto_exposure_bias',-4)
    pcamera.set_editor_property('post_process_settings',settings);pcamera.set_editor_property('post_process_blend_weight',1)
   for beam in pawn.get_components_by_class(unreal.SpotLightComponent):beam.set_visibility(False)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    if a.get_actor_label()=='Ultra_Dynamic_Weather':
     for nc in a.get_components_by_class(unreal.NiagaraComponent):nc.deactivate()
    if a.get_actor_label() in [r['name'].replace('SM_','') for r in rows]:
     mc=a.get_component_by_class(unreal.StaticMeshComponent)
     for i,s in enumerate(mc.static_mesh.static_materials):
      dry=unreal.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_Dry_'+str(s.material_slot_name));assert dry
      mc.set_material(i,dry)
     if a.get_actor_label()=='R12_OrientationProbe':
      mc.set_mobility(unreal.ComponentMobility.MOVABLE);a.set_actor_location(wp((-27,-5.6,43.2)),False,True)
   state.update(stage=3,next=time.monotonic()+12);return
  if state['stage']==3:
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/'inspection.png'));state.update(stage=4,next=time.monotonic()+4);return
  unreal.StationMigrationLibrary.set_pie_render_size(0,0);levels.editor_request_end_play();state.update(stage=5,next=time.monotonic()+2)
 except Exception:
  state['error']=traceback.format_exc();levels.editor_request_end_play();state.update(stage=5,next=time.monotonic()+2)
handle=unreal.register_slate_post_tick_callback(tick);levels.editor_request_begin_play();RESULT={'started':True}
