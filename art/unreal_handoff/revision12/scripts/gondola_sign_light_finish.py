import unreal,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.GondolaStatusSign));a.set_editor_property('unlit_strength',0)
# Off means no emitted light. The approved coloured glass still receives normal lighting.
assert ls.save_current_level();RESULT={'unlit_strength':a.unlit_strength,'lit_strength':a.lit_strength};(Path(__file__).resolve().parents[1]/'gondola_sign/light_finish.json').write_text(json.dumps(RESULT,indent=2))
