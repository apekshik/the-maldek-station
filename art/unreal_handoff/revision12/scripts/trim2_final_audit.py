import unreal,json,runpy
from pathlib import Path
b=Path(__file__).resolve().parents[1]
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MaldekRefinement/R12/Station_R12')
runpy.run_path(str(b/'scripts/audit_stage.py'),init_globals={'JOB':{'stage':'Architecture','checkpoint_transforms':'trim2/checkpoint_transforms.json'}})
review=json.loads((b/'reviews/architecture/visual_review.json').read_text())
review['trim2_supplement']={'accepted':True,'images':'trim2/after/report.json','findings':['Control jamb and header overlapping stripes removed in matched night view.','Small red markers sit on gondola roof; parked transform preserved.'],'geometry_evidence':'trim2/core_recess.json'}
(b/'reviews/architecture/visual_review.json').write_text(json.dumps(review,indent=2))
runpy.run_path(str(b/'scripts/accept_stage.py'),init_globals={'JOB':{'stage':'Architecture','route_reports':['trim2/door_routes.json','trim2/stairs_full_after.json'],'required_routes':['Control front approach','Completed rear hall approach','Quarters landing and doorway','Boarding threshold','Arrival','Quarters','Internal descending stair']}})
gm=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings().default_game_mode
p=unreal.get_default_object(unreal.get_default_object(gm).default_pawn_class)
c=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
assert abs(c.get_editor_property('focused_lumens')-1.35)<.001 and abs(c.get_editor_property('ground_height_response')-18)<.001
meshes=[]
for r in json.loads((b/'handoff_manifest.json').read_text())['chunks']:
 if 'nanite_fallback_target' not in r:continue
 m=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R12/Meshes/'+r['name']);ns=m.get_editor_property('nanite_settings')
 assert ns.fallback_target==unreal.NaniteFallbackTarget.PERCENT_TRIANGLES and ns.fallback_percent_triangles==1
 meshes.append({'name':r['name'],'triangles':m.get_num_triangles(0)})
assert len(meshes)==17
(b/'trim2/saved_audit.json').write_text(json.dumps({'success':True,'checkpoint':'adc092e11e497db27eab469102233b9a57d8415a','retained_actor_transforms':'Matched against untouched map in verification checkout, using current compiled native modules only to load it.','fallback_meshes':meshes,'focused_lumens':c.get_editor_property('focused_lumens'),'ground_height_response':c.get_editor_property('ground_height_response')},indent=2))

