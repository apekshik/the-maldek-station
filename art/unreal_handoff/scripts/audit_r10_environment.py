import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';r={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if 'Ultra_Dynamic' not in a.get_actor_label():continue
 r[a.get_actor_label()]={}
 for n in ['Moon Angle','Moon_Angle','Moon_Rotation','Moon_Inclination','Moon_Yaw','Moon_Pitch','Use_Manual_Moon_Target','Manual_Moon_Target','Moon_Target','Time_of_Day','Moon_Light_Intensity','Wind_Audio_Volume','Wind_Sound_Volume','Sound_Volume','Audio_Volume','Enable_Wind_Sound','Enable_Audio','Wind_Intensity','Wind','Wind_Sound','Wind_Volume','Sound_Effects_Volume']:
  try:r[a.get_actor_label()][n]=str(a.get_editor_property(n))
  except:pass
 task=unreal.AssetExportTask();task.object=unreal.get_default_object(a.get_class());task.filename=str(out/(a.get_class().get_name()+'_defaults.t3d'));task.exporter=unreal.ObjectExporterT3D();task.automated=True;task.prompt=False;unreal.Exporter.run_asset_export_task(task)
(out/'environment_audit.json').write_text(json.dumps(r,indent=2))
