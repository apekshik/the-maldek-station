import unreal,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
rows=[]
for a in aa.get_all_level_actors():
 label=a.get_actor_label()
 if any(x in (label+' '+a.get_class().get_name()).lower() for x in ['weather','wind','volume','audio','mig_pld','mig_plk','player']):
  rows.append({'label':label,'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'bounds':str(a.get_actor_bounds(False))})
RESULT={'pie':ls.is_in_play_in_editor(),'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name(),'actors':rows,'dirty_content':[str(p) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'dirty_maps':[str(p) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]};(O/'audio_refine/audit.json').write_text(json.dumps(RESULT,indent=2))
