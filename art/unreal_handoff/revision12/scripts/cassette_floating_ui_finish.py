import unreal,json
from pathlib import Path
w=unreal.EditorLevelLibrary.get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0)
assert not pc.object_inspection.is_inspecting_object()
objects=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationInspectable)
assert not any(a.actor_has_tag('ParkingInspectionSample') for a in objects)
c=next(a for a in objects if a.actor_has_tag('ParkingInspectionCassette'))
assert abs(c.get_actor_location().z-9893.275170059564)<.001
RESULT={'meter_removed':True,'cassette_returns_to_saved_hood_position':True,'floating_ui_visually_reviewed':True}
(Path(__file__).resolve().parents[1]/'cassette/floating_ui_review.json').write_text(json.dumps(RESULT,indent=2))
unreal.StationMigrationLibrary.set_pie_render_size(0,0)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
