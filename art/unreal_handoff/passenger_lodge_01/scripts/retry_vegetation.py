import unreal,json,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
assert not (OUT/'vegetation_moves.json').exists()
names=['FR_Understorey_034_0','FR_Understorey_036_0','FR_Understorey_037_0','FR_Understorey_042_0','FR_Understorey_042_1','FR_Understorey_043_0','FR_Understorey_083_0','FR_Understorey_086_0']
baseline=json.loads((OUT/'before.json').read_text());actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
for row in baseline['actors']:
 if row['label'] in names:actors[row['label']].set_actor_location(unreal.Vector(*row['location']),False,True)
RESULT=runpy.run_path(str(OUT/'scripts/vegetation.py'))['RESULT']
