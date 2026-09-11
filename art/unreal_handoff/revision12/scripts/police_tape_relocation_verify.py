import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();actors={a.get_actor_label():a for a in aa.get_all_level_actors()};baseline=json.loads((out/'relocation/audit.json').read_text());changed=[]
for r in baseline['actors']:
 if r['label'].startswith('PoliceTape') or r['label']=='Parking_Navigation_Sign_Light':continue
 a=actors.get(r['label']);p=a.get_actor_location() if a else None
 if not a or math.dist([p.x,p.y,p.z],r['world'])>.01:changed.append(r['label'])
assert not changed,changed
lamp=actors['Parking_Navigation_Sign_Light'];lc=lamp.get_component_by_class(unreal.SpotLightComponent);assert lc.intensity==0 and not lc.is_visible()
main=actors['PoliceTape_MainCrossing'];assert len(main.get_components_by_class(unreal.SplineMeshComponent))==72
assert len(main.tear_sounds)==3 and main.tear_attenuation
assert all(not s.get_editor_property("looping") for s in main.tear_sounds)
mesh=main.get_editor_property('ribbon_mesh');width=mesh.get_bounds().box_extent.z*2;assert abs(width-7.62)<.01
assert len([a for a in actors.values() if isinstance(a,unreal.StationPoliceTape)])==7
assert len([n for n in actors if n.startswith('PoliceTape_PerimeterTree_')])==6
assert json.loads((out/'playtest.json').read_text())['passed'];assert ls.save_current_level()
r={'saved':True,'recorded_tear_variations':3,'path_index':80,'sign_spotlight_off':True,'width_cm':width,'unrelated_actor_positions_preserved':True,'playtests_passed':True,'capture_shots':json.loads((out/'relocation/capture.json').read_text())['shots']};(out/'relocation/completion.json').write_text(json.dumps(r,indent=2));RESULT=r

