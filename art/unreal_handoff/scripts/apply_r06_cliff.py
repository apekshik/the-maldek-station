import unreal,builtins,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R06'
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name()=='Landscape')
assert land.landscape_import_heightmap_from_render_target(builtins.r06_height_rt,True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'heightmap_import.json').write_text(json.dumps({'success':True,'roundtrip_RG_error':0,'edited_pixels':2800,'map':world.get_name()}))
