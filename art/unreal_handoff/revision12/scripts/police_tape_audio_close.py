import unreal,os,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();assert ls.save_current_level();Path(__file__).resolve().parents[1].joinpath('police_tape/relocation/audio_close.json').write_text(json.dumps({'pid':os.getpid(),'saved':True}));unreal.SystemLibrary.quit_editor();RESULT={'saved':True}
