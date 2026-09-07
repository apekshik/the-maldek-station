import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision07';actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();sky=next(a for a in actors if a.get_actor_label()=='Ultra_Dynamic_Sky');task=unreal.AssetExportTask();task.object=unreal.get_default_object(sky.get_class());task.filename=str(out/'sky_defaults.t3d');task.automated=True;task.prompt=False;task.exporter=unreal.ActorExporterT3D();unreal.Exporter.run_asset_export_task(task)
