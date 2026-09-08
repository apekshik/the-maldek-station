"""Install the online CC0 key-turn recording on physical-key doors only."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
root='/Game/MaldekRefinement/R12/Doors'
t=unreal.AssetImportTask();t.filename=str(repo/'art/audio/doors/key_turn/KeyTurn.wav');t.destination_path=root+'/KeyLock/Audio';t.automated=True;t.save=True;t.replace_existing=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);sound=lib.load_asset(root+'/KeyLock/Audio/KeyTurn');assert sound
sound.set_editor_property('looping',False);sound.set_editor_property('compression_quality',100);lib.save_loaded_asset(sound)
bp=lib.load_asset(root+'/BP_StationDoor_Standard');defaults=unreal.get_default_object(bp.generated_class());defaults.set_editor_property('key_turn_sound',sound);defaults.key_inspection_light.set_intensity(.08);unreal.BlueprintEditorLibrary.compile_blueprint(bp);lib.save_loaded_asset(bp)
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StationDoor) and a.has_key_lock:
  a.set_editor_property('key_turn_sound',sound);a.set_editor_property('key_turn_volume',4.0);a.key_inspection_light.set_intensity(.08);assert not a.key_inspection_light.is_visible();rows.append(a.get_actor_label())
assert len(rows)==7;assert ls.save_current_level()
RESULT={'success':True,'doors':rows,'sound':sound.get_path_name(),'source':'https://freesound.org/people/KieranKeegan/sounds/418846/','license':'CC0-1.0'}
(b/'doors/key_lock/turn_install.json').write_text(json.dumps(RESULT,indent=2))
