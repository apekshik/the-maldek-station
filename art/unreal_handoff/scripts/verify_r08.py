"""Verify saved R08 light sources and wall attachment after reloading."""
import unreal,json
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level()
assert levels.load_level('/Game/MaldekRefinement/R08/BlockOut_R08')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
r={'disabled':[],'wall_lights':[],'wall_checks':[]}
fixture_actors=[a for a in actors if a.get_actor_label().startswith('R08_') and isinstance(a,unreal.StaticMeshActor)]
assert len(fixture_actors)==16
for fixture in fixture_actors:
 assert str(fixture.static_mesh_component.get_collision_profile_name())=='NoCollision'
for a in actors:
 label=a.get_actor_label()
 if label in ['PointLight3','R07_TestLight_Main_Platform_West','R07_TestLight_Main_Platform_East']:
  c=a.get_components_by_class(unreal.PointLightComponent)[0]
  assert c.get_editor_property('intensity')==0
  r['disabled'].append(label)
 if label.startswith('R08_WallLight_'):
  c=a.get_components_by_class(unreal.SpotLightComponent)[0]
  assert c.get_editor_property('intensity') <= 1.5
  assert c.get_editor_property('attenuation_radius')==420
  assert c.get_editor_property('outer_cone_angle')==34
  p=a.get_actor_location()
  h=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(p.x,18587.7,10553.5),unreal.Vector(p.x,18387.7,10553.5),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,fixture_actors,unreal.DrawDebugTrace.NONE).to_tuple()
  assert h[0], 'No mounting wall behind '+label
  assert abs(h[5].y-18485.7)<5, 'Mount is not flush with expected wall face: '+str(h[5])
  r['wall_checks'].append({'label':label,'hit':True,'wall_face_cm':[h[5].x,h[5].y,h[5].z]})
  r['wall_lights'].append({'label':label,'lumens':c.get_editor_property('intensity'),'radius_cm':420,'outer_cone_degrees':34})
 if label=='Ultra_Dynamic_Sky':
  r['time_of_day']=a.get_editor_property('Time of Day')
  r['moon_intensity']=a.get_editor_property('Moon Light Intensity')
assert len(r['disabled'])==3 and len(r['wall_lights'])==2
assert abs(r['time_of_day']-2300)<.01
assert abs(r['moon_intensity']-.15)<.001
(Path(__file__).resolve().parents[1]/'revision08/reload_verification.json').write_text(json.dumps(r,indent=2))
