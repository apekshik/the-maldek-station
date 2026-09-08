import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
plan=json.loads((out/'plan.json').read_text());n=plan['nodes'][0];floor=(n['z']-plan['rope_offset_m'])*100
eye=unreal.Vector(n['x']*100+150,n['y']*100-600,floor+170);target=unreal.Vector(n['x']*100,n['y']*100+1500,floor+160)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
runtime=json.loads((out/'runtime.json').read_text());reopen=json.loads((out/'reopen.json').read_text());clearance=json.loads((out/'clearance.json').read_text());inspection=json.loads((out/'views/inspection.json').read_text())
assert runtime['passed'] and reopen['passed'] and inspection['passed'] and not clearance['collisions']
RESULT={'complete':True,'level':'/Game/MaldekRefinement/R12/Station_R12','length_m':reopen['length_m'],'pylons':5,'arrival_seconds':runtime['arrival_seconds'],'outbound_seconds':runtime['outbound_seconds'],'return_seconds':runtime['return_seconds'],'occupied_bridge_held':runtime['occupied_bridge_held'],'poses_checked':clearance['poses'],'terrain_samples_unchanged':reopen['terrain_samples'],'saved_and_reopened':True,'inspection_light_removed':not any(a.get_actor_label()=='Gondola_Inspection_Temporary' for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())}
assert RESULT['inspection_light_removed'];(out/'completion.json').write_text(json.dumps(RESULT,indent=2))
