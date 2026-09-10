import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin']
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
p=wp(JOB.get('position',[-36,-30,19]));target=wp(JOB.get('target',[-16,-4,4]))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,target))
RESULT={'camera':str(p)}
