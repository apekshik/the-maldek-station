import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin']
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
p=wp([-15.8,-16.35,1.7]);target=wp([-23,-16.35,4.8])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,target))
RESULT={'view':'arrival stair ascent'}
