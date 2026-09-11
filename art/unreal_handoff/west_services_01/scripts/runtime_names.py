import unreal,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];w=unreal.EditorLevelLibrary.get_game_world();aa=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor);RESULT={a.get_name():a.get_actor_label() for a in aa if a.get_actor_label().startswith('MIG_WS_')};(P/'runtime_names.json').write_text(json.dumps(RESULT,indent=2));RESULT={'names':len(RESULT)}
