import unreal,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();gm=w.get_world_settings().default_game_mode;pc=unreal.get_default_object(gm).default_pawn_class
materials={}
for a in aa.get_all_level_actors():
 if a.get_actor_label().startswith('MIG_'):
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   for m in c.get_materials():
    if m and any(x in m.get_name().lower() for x in ['floor','quarry','tile']):materials[m.get_path_name()]=str(m.get_editor_property('phys_material'))
weather=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Weather');props={}
for k in ['Wind Intensity','Wind_Intensity','wind_intensity','Snow','snow','Weather','weather']:
 try:props[k]=str(weather.get_editor_property(k))
 except Exception:pass
RESULT={'pawn':pc.get_path_name(),'materials':materials,'weather':props};(O/'audio_refine/targets.json').write_text(json.dumps(RESULT,indent=2))
