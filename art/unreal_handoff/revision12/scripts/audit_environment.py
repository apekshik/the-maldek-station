import unreal,json,re
from pathlib import Path
base=Path(__file__).resolve().parents[1];levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not levels.is_in_play_in_editor();levels.save_current_level()
report={}
fields=['Weather','Snow','Rain','Fog','Cloud Coverage','Wind Intensity','Material Snow Coverage','Material Wetness','Begin Play Weather is Random','Random Weather Variation','Weather Sounds Master Volume','Wind Volume','Time Of Day','Time of Day','Simulate Real Sun','Animate Time Of Day','Season']
for name in [JOB.get('name','r12')]:
 rows={}
 for a in aa.get_all_level_actors():
  if a.get_actor_label() not in ['Ultra_Dynamic_Weather','Ultra_Dynamic_Sky']:continue
  row={}
  for f in fields:
   try:row[f]=str(a.get_editor_property(f))
   except Exception:pass
  rows[a.get_actor_label()]=row
  task=unreal.AssetExportTask();task.object=a;task.filename=str(base/(name+'_'+a.get_actor_label()+'.t3d'));task.automated=True;task.prompt=False;task.exporter=unreal.ActorExporterT3D();unreal.Exporter.run_asset_export_task(task)
 report[name]=rows
(base/(name+'_environment.json')).write_text(json.dumps(report,indent=2));RESULT=report
