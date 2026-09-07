"""Read-only progress snapshot while the asynchronous movement driver runs."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1]
w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
v=p.get_actor_location() if p else None
RESULT={'pie':bool(w),'player_local_metres':[(o[0]-v.x)/100,(v.y-o[1])/100,(v.z-o[2])/100] if v else None}
