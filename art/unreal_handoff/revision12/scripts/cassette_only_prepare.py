import unreal,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=list(aa.get_all_level_actors())
cassette=next(a for a in actors if a.actor_has_tag('ParkingInspectionCassette'));pose=cassette.get_actor_transform()
meters=[a for a in actors if a.actor_has_tag('ParkingInspectionSample')]
removed=[a.get_actor_label() for a in meters]
for a in meters:assert aa.destroy_actor(a)
assert cassette.get_actor_transform()==pose
assert ls.save_current_level()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'removed':removed,'cassette_preserved':True,'saved':True}
(Path(__file__).resolve().parents[1]/'cassette/meter_removal.json').write_text(json.dumps(RESULT,indent=2))
unreal.SystemLibrary.quit_editor()
