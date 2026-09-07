import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';r={}
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 if 'Ultra_Dynamic' not in a.get_actor_label():continue
 d={}
 for n in ['Fog','Fog Density','Fog_Density','Fog_Density_Multiplier','Base_Fog_Density','Fog_Base_Density','Volumetric_Fog','Use_Volumetric_Fog','Snow','Snow_Coverage','Snow_Coverage_Amount','Cloud_Coverage','Time_of_Day','Fog_Amount','Overall_Fog_Density','Fog_Max_Opacity']:
  try:d[n]=str(a.get_editor_property(n))
  except:pass
 r[a.get_actor_label()]=d
r['exporters']=[n for n in dir(unreal) if 'Exporter' in n and any(s in n for s in ['Actor','Text','Level'])]
(out/'weather_fields.json').write_text(json.dumps(r,indent=2))
