import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
routes=json.loads((out/'routes.json').read_text());reopen=json.loads((out/'reopen.json').read_text());capture=json.loads((out/'final/capture.json').read_text())
assert routes['success'] and len(routes['results'])==8 and reopen['passed'] and reopen['reopened'] and capture['success']
assert len(capture['images'])==4 and abs(reopen['sign_light_lumens'])<.001
assert all(Path(p).is_file() for p in capture['images'])
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();assert not any(a.get_actor_label()=='R12_Transient_Review_Lamp' for a in actors)
o=json.loads((out/'before.json').read_text())['origin']
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
eye=wp([-35,-60.5,.65]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,wp([-33,-51,.4])))
RESULT={'complete':True,'saved_and_reopened':True,'level':'/Game/MaldekRefinement/R12/Station_R12','opening_width_m':3.2,'walking_tests_passed':8,'walking_tests_total':8,'maximum_airborne_seconds':max(r['max_airborne_seconds'] for r in routes['results']),'terrain_clearance_samples':len(reopen['samples']),'minimum_terrain_clearance_m':reopen['minimum_terrain_clearance_m'],'review_images':capture['images'],'temporary_light_removed':True,'preserved':reopen['preserved'],'delivery_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'fbx').glob('*.fbx')}}
(out/'completion.json').write_text(json.dumps(RESULT,indent=2))
