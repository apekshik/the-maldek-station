import unreal,json,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert ls.save_current_level()
assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
site=runpy.run_path(str(OUT/'scripts/verify_site.py'))['RESULT']
routes=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT']
assert site['stair_ground_clear'] and not routes['failures']
RESULT={'reopened':True,'original_map_unchanged':site['original_map_unchanged'],'actor_errors':site['actor_errors'],'stair_ground_probes':len(site['stair_ground_probes']),'route_samples':routes['samples'],'route_failures':routes['failures']}
(OUT/'reopen_verification.json').write_text(json.dumps(RESULT,indent=2))
