"""Import native-referenced recorded audio without changing the station map."""
import unreal,json
from pathlib import Path
repo=Path(__file__).resolve().parents[4];root='/Game/MaldekRefinement/R12/GondolaArrival';rows=[]
for source in sorted((repo/'art/audio/gondola_arrival/wav').glob('*.wav')):
 task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=root;task.automated=True;task.save=True;task.replace_existing=True
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 sound=unreal.EditorAssetLibrary.load_asset(root+'/'+source.stem);assert sound
 sound.set_editor_property('looping',False);sound.set_editor_property('volume',1.0);sound.set_editor_property('compression_quality',100)
 unreal.EditorAssetLibrary.save_loaded_asset(sound);rows.append(sound.get_path_name())
assert len(rows)==5
(repo/'art/audio/gondola_arrival/import.json').write_text(json.dumps({'success':True,'sounds':rows},indent=2))
