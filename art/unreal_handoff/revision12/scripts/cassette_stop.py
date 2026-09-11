import unreal,json
from pathlib import Path
w=unreal.EditorLevelLibrary.get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0);pc.object_inspection.cancel_inspection()
unreal.StationMigrationLibrary.set_pie_render_size(0,0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));settings.set_editor_property('bThrottleCPUWhenNotForeground',True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();RESULT={'stopped':True}
