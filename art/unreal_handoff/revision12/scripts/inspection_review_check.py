import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'inspection'
state=json.loads((out/'mouse_review.json').read_text())
w=unreal.EditorLevelLibrary.get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0)
obj=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationInspectable) if a.actor_has_tag('ParkingInspectionSample'))
if JOB.get('action')=='finish':
 assert not pc.object_inspection.is_inspecting_object(),'Return the prop before finishing'
 assert not pc.is_move_input_ignored() and not pc.is_look_input_ignored()
 original=json.loads((out/'parking_install.json').read_text())['location']
 assert (obj.get_actor_location()-unreal.Vector(*original)).length()<.001
 state['mouse_session_return_restored']=True
 unreal.StationMigrationLibrary.set_pie_render_size(0,0)
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
 settings.set_editor_property('bThrottleCPUWhenNotForeground',state['previous_throttle'])
 unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
else:
 after=obj.get_actor_transform().rotation.to_tuple();before=state['rotation_before_drag']
 state['rotation_after_drag']=after
 state['actual_mouse_drag_rotates']=abs(sum(a*b for a,b in zip(before,after)))<.999
 state['mouse_session_keeps_input_locked']=pc.is_move_input_ignored() and pc.is_look_input_ignored()
 assert state['actual_mouse_drag_rotates'],'No rotation from actual mouse drag'
(out/'mouse_review.json').write_text(json.dumps(state,indent=2))
RESULT=state
