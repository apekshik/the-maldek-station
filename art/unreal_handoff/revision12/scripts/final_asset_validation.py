"""Remove exactly the rejected probe assets and validate the saved release assets."""
import unreal,runpy,json
from pathlib import Path
b=Path(__file__).resolve().parents[1]
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
deleted=[]
for name in ['SM_TerrainNaniteProbe','MI_TerrainNaniteProbe','M_TerrainNaniteProbe']:
 path='/Game/MaldekRefinement/R12/Diagnostics/'+name
 if unreal.EditorAssetLibrary.does_asset_exist(path):
  assert unreal.EditorAssetLibrary.delete_asset(path),path
  deleted.append(path)
(b/'diagnostic_asset_cleanup.json').write_text(json.dumps({'deleted':deleted,'level_bindings_changed':False},indent=2))
runpy.run_path(str(b/'scripts/validate_references.py'))
runpy.run_path(str(b/'scripts/accept_integrated_stages.py'))
RESULT={'success':True}
