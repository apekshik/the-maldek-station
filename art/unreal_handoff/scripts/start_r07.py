"""Open or create R07, apply its atmosphere, and start the local review dispatcher."""
from pathlib import Path
import runpy
import unreal

scripts = Path(__file__).resolve().parent
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
map_path = '/Game/MaldekRefinement/R07/BlockOut_R07'
if unreal.EditorAssetLibrary.does_asset_exist(map_path):
    assert levels.load_level(map_path)
else:
    assert levels.new_level_from_template(map_path, '/Game/MaldekRefinement/R06/BlockOut_R06')
runpy.run_path(str(scripts / 'set_r07_local_fog.py'))
runpy.run_path(str(scripts / 'place_r07_lighting_study.py'))
runpy.run_path(str(scripts / 'review_session.py'))
