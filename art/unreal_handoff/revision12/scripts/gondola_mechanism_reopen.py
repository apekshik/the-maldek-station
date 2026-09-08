import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_mechanism';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert not any(a.get_actor_label()=='Gondola_Inspection_Temporary' for a in aa.get_all_level_actors())
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');start=time.monotonic()
def verify(dt):
 if time.monotonic()-start<8:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];m=actors['R12_Gondola_Mechanism'];assert m.gondola==g and len(m.rotors)==84 and len(m.rope_parts)==1 and len(m.sound_sources)==9
  assert all(r.actor and r.actor.get_component_by_class(unreal.StaticMeshComponent).static_mesh for r in m.rotors)
  assert len(g.cabin_parts)==24 and (g.far_boarding_bridge.get_actor_location()-g.far_bridge_parked).length()<.1
  for i in range(2):assert actors['R12_Gondola_Interior_Light_%d'%i].point_light_component.intensity==12
  mat=unreal.load_asset('/Game/MaldekRefinement/R12/GondolaRoute/Materials/MI_Gondola_Lamp_Dim');assert abs(unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mat,'EmissionStrength')-.6)<.001
  for label in ['R12_Route_Terminal_Millford','R12_Route_Terminal_Maldek','R12_Route_Cable_Passenger','R12_Route_Cable_Return','R12_04_Lower_Drive_001_thin','R12_04_Lower_Drive_004_signage']:assert not actors[label].static_mesh_component.static_mesh
  movingmat=unreal.load_asset('/Game/MaldekRefinement/R12/GondolaMechanism/Materials/M_Moving_Rope');errors=list(unreal.StationMigrationLibrary.validate_material_shaders([movingmat]));assert not errors,errors
  mesh=m.rope_parts[0].static_mesh_component.static_mesh;settings=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_lod_build_settings(mesh,0);assert settings.get_editor_property('use_full_precision_u_vs')
  survey=json.loads((b/'gondola_route/survey.json').read_text());terrain=[actors[n] for n in survey['terrain']];ignore=[a for a in actors.values() if a not in terrain];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();deltas=[]
  for row in survey['samples']:
   x,y=row['xy'];hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,180000),unreal.Vector(x,y,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE);assert hit.to_tuple()[0];deltas.append(abs(hit.to_tuple()[5].z-row['centre'][2]))
  assert max(deltas)<.1
  for source in m.sound_sources:
   c=source.actor.get_component_by_class(unreal.AudioComponent);a=c.get_editor_property('attenuation_overrides');assert a.spatialize and a.attenuate and a.enable_occlusion and c.sound.get_editor_property('looping')
  eye=unreal.Vector(-44132,18679,10468);target=unreal.Vector(-44282,20800,10458);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target));assert ls.save_current_level()
  capture_restore=dict(unreal.StationMigrationLibrary.set_pie_audio_capture_enabled(False));assert capture_restore['UnfocusedBefore']==0
  report={'audio_capture_override_restored':True,'passed':True,'reopened':True,'rotors':84,'sound_sources':9,'continuous_rope':True,'full_precision_uv':True,'shader_errors':errors,'old_geometry_retired':True,'cabin_lighting_preserved':True,'terrain_samples':len(deltas),'max_terrain_change_cm':max(deltas),'bridge_parked':True}
 except Exception:report={'passed':False,'error':traceback.format_exc()}
 (out/'reopen.json').write_text(json.dumps(report,indent=2))
handle=unreal.register_slate_post_tick_callback(verify);RESULT={'started':True}
