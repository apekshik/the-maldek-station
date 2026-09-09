import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_sign';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor()
assert not any(a.get_actor_label()=='Sign_Inspection_Temporary' for a in aa.get_all_level_actors())
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');start=time.monotonic()
def verify(dt):
 if time.monotonic()-start<8:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  by={a.get_actor_label():a for a in aa.get_all_level_actors()};a=by['R12_Gondola_Status_Sign'];g=by['BP_GondolaSystem'];sp=g.get_components_by_class(unreal.SplineComponent)[0]
  assert a.gondola==g and not a.far_terminal and a not in g.cabin_parts and not a.get_attach_parent_actor()
  assert a.unlit_strength==0 and a.lit_strength==11
  assert len(a.circuits)==4 and all(c.static_mesh and c.get_num_materials()==1 for c in a.circuits)
  assert unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_convex_collision_count(a.cabinet.static_mesh)==3
  assert all(c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION for c in a.circuits)
  origin=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);heading=sp.get_location_at_distance_along_spline(2000,unreal.SplineCoordinateSpace.WORLD)-origin;offset=a.get_actor_location()-origin
  left=unreal.Vector(heading.y,-heading.x,0);assert unreal.MathLibrary.dot_vector_vector(offset,left)<0,'Sign is not on the right-hand roof'
  assert abs(offset.x+350)<.01 and abs(offset.y+250)<.01 and abs(offset.z-360)<.01
  assert abs(a.get_actor_rotation().yaw+90)<.01
  assert g.stage_first_arrival and g.wait_time_at_maldek==180
  assert by['R12_Gondola_Mechanism'] not in g.cabin_parts
  assert any('Parking_Navigation' in label for label in by),'Existing parking changes were lost'
  assert not unreal.StationMigrationLibrary.validate_material_shaders([c.get_material(0) for c in a.circuits])
  report={'passed':True,'reopened':True,'sign_position':a.get_actor_location().to_tuple(),'right_hand_roof_facing_left':True,'heading':heading.to_tuple(),'collision_hulls':3,'four_circuits_saved':True,'parking_changes_preserved':True,'temporary_light_removed':True,'default_dwell_preserved':True}
 except Exception:report={'passed':False,'error':traceback.format_exc()}
 (out/'reopen.json').write_text(json.dumps(report,indent=2))
handle=unreal.register_slate_post_tick_callback(verify);RESULT={'started':True}
