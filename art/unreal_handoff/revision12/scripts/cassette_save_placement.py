import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
a=next(a for a in aa.get_all_level_actors() if a.actor_has_tag('ParkingInspectionCassette'))
p=Path(__file__).resolve().parents[4]/'art/blender/cassette_01/unreal_install.json';report=json.loads(p.read_text());loc=unreal.Vector(*report['location']);loc.z=9893.275170059564
a.set_actor_location(loc,False,True)
assert ls.save_current_level();report['location']=loc.to_tuple();report['visual_hood_clearance_cm']=6;report['saved']=True;p.write_text(json.dumps(report,indent=2));RESULT=report
