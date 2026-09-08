import unreal,json,time,runpy,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
assert not any(a.get_actor_label()=='Gondola_Inspection_Temporary' for a in aa.get_all_level_actors())
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');start=time.monotonic()
def finish(dt):
 if time.monotonic()-start<8:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];assert len(g.cabin_parts)==24 and g.stage_first_arrival and g.far_boarding_bridge
  assert (g.far_boarding_bridge.get_actor_location()-g.far_bridge_parked).length()<.1
  for i in range(2):assert actors['R12_Gondola_Interior_Light_%d'%i].point_light_component.intensity==12
  dim=unreal.load_asset('/Game/MaldekRefinement/R12/GondolaRoute/Materials/MI_Gondola_Lamp_Dim')
  assert abs(unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(dim,'EmissionStrength')-.6)<.001
  for label,a in actors.items():
   if label.startswith(('R12_Route_Pylon_','R12_Route_Cable_','R12_Route_Terminal_')) or label=='R12_Gondola_Hanger_Adapter':
    r=a.get_actor_rotation();assert abs(abs(r.yaw)-180)<.01 and abs(r.pitch)<.01 and abs(r.roll)<.01,(label,str(r))
  survey=json.loads((out/'survey.json').read_text());terrain=[actors[n] for n in survey['terrain']];ignore=[a for a in actors.values() if a not in terrain];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();errors=[]
  for row in survey['samples']:
   x,y=row['xy'];h=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,180000),unreal.Vector(x,y,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE);assert h.to_tuple()[0];errors.append(abs(h.to_tuple()[5].z-row['centre'][2]))
  assert max(errors)<.1,max(errors)
  report=runpy.run_path(str(b/'scripts/gondola_route_verify.py'))['RESULT'];report.update(passed=True,reopened=True,terrain_samples=len(errors),max_terrain_change_cm=max(errors),gangway_parked=True,interior_lights_verified=True)
 except Exception:report={'passed':False,'error':traceback.format_exc()}
 (out/'reopen.json').write_text(json.dumps(report,indent=2))
handle=unreal.register_slate_post_tick_callback(finish);RESULT={'reopened':True}
