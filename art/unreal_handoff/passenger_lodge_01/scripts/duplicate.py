"""Create the isolated migration map from the saved current station."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]; REPO=OUT.parents[2]
baseline=json.loads((OUT/'before.json').read_text())
original=REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap'
assert hashlib.sha256(original.read_bytes()).hexdigest()==baseline['map_sha256']
target='/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert not unreal.EditorAssetLibrary.does_asset_exist(target), 'Migration map already exists; inspect before resuming.'
assert levels.new_level_from_template(target,'/Game/MaldekRefinement/R12/Station_R12')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
actual={a.get_name():a for a in actors}; errors=[]
for row in baseline['actors']:
 a=actual.get(row['name'])
 if not a: errors.append(row['name']+': missing'); continue
 p=a.get_actor_location(); r=a.get_actor_rotation(); s=a.get_actor_scale3d()
 for key,values in [('location',[p.x,p.y,p.z]),('rotation',[r.pitch,r.yaw,r.roll]),('scale',[s.x,s.y,s.z])]:
  if max(abs(x-y) for x,y in zip(values,row[key]))>0.001:errors.append(row['name']+': '+key)
assert not errors, errors
assert len(actors)==baseline['actor_count']
assert levels.save_current_level()
assert hashlib.sha256(original.read_bytes()).hexdigest()==baseline['map_sha256']
RESULT={'target':target,'actors':len(actors),'transform_errors':errors,'original_unchanged':True}
(OUT/'duplicate.json').write_text(json.dumps(RESULT,indent=2))
