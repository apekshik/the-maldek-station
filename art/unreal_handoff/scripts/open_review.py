import unreal,runpy
from pathlib import Path
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MaldekRefinement/Maps/BlockOut_R04')
runpy.run_path(str(Path(__file__).with_name('review_session.py')))
runpy.run_path(str(Path(__file__).with_name('verify_working_level.py')))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-46500,21200,11800),unreal.Rotator(pitch=-25,yaw=-45,roll=0))

