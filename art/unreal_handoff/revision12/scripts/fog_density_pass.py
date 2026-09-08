"""A modest scene-wide fog increase, preserving weather, color and exposure."""
import json,unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'fog_density';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sky=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
fields=['Scale Fog Density','Fog','Use Volumetric Fog','Fog Color Intensity Scale','Volumetric Fog Distance','Volumetric Fog Extinction','Time Of Day','Cloud Coverage']
before={k:sky.get_editor_property(k) for k in fields}
if not JOB.get('apply'):
 RESULT={'settings':before}
else:
 # Store a fixed target so rerunning the pass cannot keep multiplying density.
 path=out/'settings.json'
 if path.exists():target=json.loads(path.read_text())['after']['Scale Fog Density']
 else:target=float(before['Scale Fog Density'])*1.3
 assert target>0
 sky.set_editor_property('Scale Fog Density',target)
 after={k:sky.get_editor_property(k) for k in fields}
 assert all(after[k]==v for k,v in before.items() if k!='Scale Fog Density')
 assert abs(after['Scale Fog Density']-target)<.0001
 assert ls.save_current_level()
 RESULT={'success':True,'before':before,'after':after,'density_multiplier':1.3,'changed_property':'Scale Fog Density'}
 path.write_text(json.dumps(RESULT,indent=2))
