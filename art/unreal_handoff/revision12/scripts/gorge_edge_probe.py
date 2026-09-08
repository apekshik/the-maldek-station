"""Read current ground around the entire local mesh perimeter."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.Landscape))
bounds=[502,1485,714,1740];data=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,-1));assert data
(out/'edge_probe.json').write_text(json.dumps({'bounds':bounds,'current':data}));RESULT={'read':len(data)}
