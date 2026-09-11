import unreal
m=unreal.load_asset('/Game/Inspection/Cassette/SM_ServiceCassette')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(a for a in aa.get_all_level_actors() if a.actor_has_tag('ParkingInspectionCassette'))
RESULT={'mesh_bounds':str(m.get_bounds()),'actor_bounds':str(a.get_actor_bounds(False)),'loc':str(a.get_actor_location()),'upface':str(a.get_actor_right_vector())}
