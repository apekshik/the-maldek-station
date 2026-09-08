import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};survey=json.loads((out/'survey.json').read_text())
for i in range(2):
 c=actors['R12_Gondola_Interior_Light_%d'%i].point_light_component;c.set_intensity(12);c.set_volumetric_scattering_intensity(.025)
# Leave clearance between the stopped cabin nose and the retained distant facade.
station=actors['R10_Distant_Station'];p=station.get_actor_location();delta=survey['remote'][1]+100-p.y
for label,a in actors.items():
 if label=='R10_Distant_Station' or label.startswith('R10_Distant_Window_'):a.set_actor_location(a.get_actor_location()+unreal.Vector(0,delta,0),False,True)
assert ls.save_current_level();RESULT={'saved':True,'interior_lumens_each':12,'distant_facade_shift_cm':100};(out/'finish.json').write_text(json.dumps(RESULT,indent=2))
