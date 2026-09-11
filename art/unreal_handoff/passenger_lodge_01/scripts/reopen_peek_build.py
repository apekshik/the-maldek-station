import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]
runpy.run_path(str(out/'scripts'/'session.py'))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
doors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StationDoor)
rows=[{'name':d.get_actor_label(),'key_fov':d.get_editor_property('key_closeup_fov'),'keypad_fov':d.get_editor_property('keypad_closeup_fov'),'peek_degrees':d.get_editor_property('peek_yaw_degrees'),'peek_roll':d.get_editor_property('peek_roll_degrees'),'peek_fov':d.get_editor_property('peek_fov')} for d in doors]
assert 'Station_Lodge_Migration' in world.get_path_name()
assert rows and all(r['peek_degrees']==95 and r['peek_roll']==8 and r['peek_fov']==85 and r['key_fov']==56 and r['keypad_fov']==64 for r in rows)
(out/'peek_95_reopen.json').write_text(json.dumps({'world':world.get_path_name(),'peek_loaded':True,'doors':rows},indent=2))


