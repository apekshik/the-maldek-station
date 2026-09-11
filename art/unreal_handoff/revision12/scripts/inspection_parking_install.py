"""Seat a persistent inspectable meter on the pickup hood and save a development checkpoint."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'inspection';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/MaldekRefinement/R12/Station_R12.')
actors=list(aa.get_all_level_actors())
before={a.get_path_name():a.get_actor_transform() for a in actors}
truck=next(a for a in actors if a.get_actor_label()=='FR_Parked_Pickup')
def trace(p,ignore):
 hit=unreal.SystemLibrary.line_trace_single(world,p+unreal.Vector(0,0,350),p-unreal.Vector(0,0,350),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 assert hit and hit.to_tuple()[0],'No supporting surface'
 return hit.to_tuple()
surface=trace(unreal.MathLibrary.transform_location(truck.get_actor_transform(),unreal.Vector(175,-45,0)),[a for a in actors if a!=truck])
normal=surface[6]
rotation=unreal.Rotator(roll=8.221,yaw=truck.get_actor_rotation().yaw-90)
obj=next((a for a in actors if a.actor_has_tag('ParkingInspectionSample')),None)
if obj is None:obj=aa.spawn_actor_from_class(unreal.StationInspectable,surface[5],rotation)
obj.set_actor_label('Inspection_Meter_Pickup_Hood');obj.set_folder_path('R12/Inspection')
obj.tags=['ParkingInspectionSample'];obj.mesh.set_static_mesh(unreal.load_asset('/Game/Inspection/SM_InspectionMeter'))
obj.set_actor_rotation(rotation,False);obj.set_actor_scale3d(unreal.Vector(1,1,1))
obj.set_actor_location(surface[5]+normal*.25,False,True)
obj.set_editor_property('display_name','Millford service meter')
obj.set_editor_property('description','Cable tension diagnostic unit. Turn it over to read the service marking.')
obj.set_editor_property('inspection_rotation',unreal.Rotator(yaw=90))
obj.mesh.set_simulate_physics(False)
standing=unreal.MathLibrary.transform_location(truck.get_actor_transform(),unreal.Vector(320,-45,0))
ground=trace(standing,[truck,obj])
standing.z=ground[5].z+98
target=obj.get_actor_bounds(False)[0]
view=unreal.MathLibrary.find_look_at_rotation(standing+unreal.Vector(0,0,64),target)
marker=next((a for a in actors if a.actor_has_tag('InspectionTestCheckpoint')),None)
if marker is None:marker=aa.spawn_actor_from_class(unreal.TargetPoint,standing,view)
marker.set_actor_label('Inspection_Parking_Checkpoint');marker.tags=['InspectionTestCheckpoint'];marker.set_folder_path('R12/Inspection')
marker.set_actor_location_and_rotation(standing,view,False,True)
for actor in actors:
 if actor not in [obj,marker]:assert actor.get_actor_transform()==before[actor.get_path_name()],actor.get_actor_label()
assert ls.save_current_level()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(standing+unreal.Vector(0,0,64),view)
aa.set_selected_level_actors([obj])
RESULT={'saved':True,'level':world.get_path_name(),'label':obj.get_actor_label(),'vehicle':truck.get_actor_label(),'placement':'front hood, near the corner','location':obj.get_actor_location().to_tuple(),'rotation':obj.get_actor_rotation().to_tuple(),'checkpoint_location':standing.to_tuple(),'checkpoint_rotation':view.to_tuple(),'surface_normal':normal.to_tuple(),'other_actor_transforms_preserved':True}
(out/'parking_install.json').write_text(json.dumps(RESULT,indent=2))
