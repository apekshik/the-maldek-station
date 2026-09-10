import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='InstancedFoliageActor0')
native=dict(unreal.StationMigrationLibrary.get_foliage_instance_transforms(a))
rows={k:[t.translation.x,t.translation.y,t.translation.z] for k,t in native.items()}
(OUT/'cleanup_foliage_checkpoint.json').write_text(json.dumps(rows));RESULT={'instances':len(rows),'purpose':'Post-cleanup checkpoint for save/reopen validation'}
