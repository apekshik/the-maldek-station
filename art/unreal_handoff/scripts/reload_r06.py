import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1];levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level();assert levels.load_level('/Game/MaldekRefinement/R06/BlockOut_R06')
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();r={'foliage_instances':sum(c.get_instance_count() for x in a for c in x.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)),'fog':{},'map':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()}
for x in a:
 if 'Ultra_Dynamic' in x.get_actor_label():r['fog'][x.get_actor_label()]=float(x.get_editor_property('Fog'))
(out/'revision06/reload_verification.json').write_text(json.dumps(r,indent=2));runpy.run_path(str(Path(__file__).with_name('verify_r06_cliff.py')))
