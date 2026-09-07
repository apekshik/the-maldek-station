import unreal,json
from pathlib import Path
sky=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
r={}
for k,v in {'Moon Light Intensity':.6,'Sky Light Intensity':1.5}.items():
 r[k]={'before':str(sky.get_editor_property(k)),'after':v};sky.set_editor_property(k,v)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(Path(__file__).resolve().parents[1]/'revision07/ambient_adjustment.json').write_text(json.dumps(r,indent=2))
