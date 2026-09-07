"""Create the R12 copy once. Never recreate an existing migration level on rerun."""
import unreal,json,hashlib,re
from pathlib import Path
base=Path(__file__).resolve().parents[1]
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib=unreal.EditorAssetLibrary
assert not levels.is_in_play_in_editor()
source='/Game/MaldekRefinement/ForestTest/Forest_Approach_Test'
target='/Game/MaldekRefinement/R12/Station_R12'
assert json.loads((base/'baseline/performance_capture.json').read_text())['success'],'Capture baseline before copying the map'
if not lib.does_asset_exist(target):
 assert levels.save_current_level()
 assert levels.new_level_from_template(target,source)
else:assert levels.load_level(target)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='Station_R12'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
checkpoint=json.loads((base.parents[1]/'checkpoints/pre_vf07/unreal_saved.json').read_text())
old={r['label']:r for r in checkpoint['actors']}
rows=[]
for a in actors:
 label=a.get_actor_label();prior=old.get(label)
 assert prior,('Unexpected baseline actor',label)
 clean=lambda text:re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',text)
 assert clean(str(a.get_actor_transform()))==clean(prior['transform']),('Transform changed while copying',label)
 rows.append({'label':label,'source_path':prior['path'],'r12_path':a.get_path_name(),'transform':str(a.get_actor_transform()),'treatment':'preserve','components':prior['components']})
assert len(rows)==len(old)
path=base/'replacement_inventory.json'
if not path.exists():path.write_text(json.dumps(rows,indent=2))
assert levels.save_current_level()
RESULT={'level':world.get_path_name(),'preserved_actors':len(rows),'saved':True}
(base/'level_established.json').write_text(json.dumps(RESULT,indent=2))
