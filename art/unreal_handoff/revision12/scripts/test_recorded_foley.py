"""Reuse actual-movement coverage with the R12 pawn and recorded sound banks."""
from pathlib import Path
base=Path(__file__).resolve().parents[2]
test_out=base/'revision12/recorded_foley_test';test_out.mkdir(exist_ok=True)
source=(base/'scripts/test_forest_audio.py').read_text()
source=source.replace('assert not levels.is_in_play_in_editor();assert levels.save_current_level()', 'assert not levels.is_in_play_in_editor();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()')
source=source.replace('levels.save_current_level();unreal.unregister_slate_post_tick_callback(audio_test_handle)', "unreal.EditorLevelLibrary.load_level('/Game/MaldekRefinement/R12/Station_R12');unreal.unregister_slate_post_tick_callback(audio_test_handle)")
source=source.replace("out=Path(__file__).resolve().parents[1]/'forest_test'",'out=Path('+repr(str(test_out))+')')
source=source.replace("out.parent/'working_level_report.json'",'Path('+repr(str(base/'working_level_report.json'))+')')
source=source.replace("out.parent/'revision10/approach_path.json'",'Path('+repr(str(base/'revision10/approach_path.json'))+')')
source=source.replace('assert len(c.soil_steps)==5 and len(c.metal_steps)==5',"assert len(c.soil_steps)==18 and len(c.metal_steps)==15\n   assert all('/RecordedFoley/' in s.get_path_name() for bank in [c.soil_steps,c.gravel_steps,c.metal_steps,c.concrete_steps,c.wood_steps] for s in bank)\n   state['pawn']=pawn.get_class().get_path_name()\n   state['banks']={k:[s.get_path_name() for s in c.get_editor_property(k+'_steps')] for k in ['soil','gravel','metal','concrete','wood']}")
exec(compile(source,str(base/'scripts/test_forest_audio.py'),'exec'),globals())
RESULT={'started':True,'report':str(test_out/'audio_validation.json')}
