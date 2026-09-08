"""User-requested daytime inspection, with exact restoration of sky settings."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
sky=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
path=out/'night_sky_settings.json'
if JOB.get('restore'):
 original=json.loads(path.read_text())
 for k,v in original.items():sky.set_editor_property(k,v)
 assert all(sky.get_editor_property(k)==v for k,v in original.items())
 assert ls.save_current_level();RESULT={'restored':original}
else:
 fields=['Time Of Day','Animate Time Of Day','Simulate Real Sun','Scale Fog Density','Cloud Coverage']
 if not path.exists():path.write_text(json.dumps({k:sky.get_editor_property(k) for k in fields},indent=2))
 sky.set_editor_property('Time Of Day',1300.0);sky.set_editor_property('Animate Time Of Day',False);sky.set_editor_property('Simulate Real Sun',False)
 assert ls.save_current_level();RESULT={'daytime':sky.get_editor_property('Time Of Day')}
