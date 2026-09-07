import unreal,json,re
from pathlib import Path
out=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/trim2/checkpoint_transforms.json')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MaldekRefinement/R12/Station_R12')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
out.write_text(json.dumps({a.get_path_name():re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',str(a.get_actor_transform())) for a in actors},indent=2))
