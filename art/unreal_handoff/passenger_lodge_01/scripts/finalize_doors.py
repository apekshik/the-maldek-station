"""Save closed review state after temporary lighting has been removed."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'doors';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
assert not any(a.get_actor_label().startswith('Lodge_Surface_Review_Temporary') for a in actors)
doors=[a for a in actors if a.get_actor_label().startswith('MIG_PLD_')];assert len(doors)==3
for a in doors:
 assert a.is_locked() and a.key_available and abs(a.hinge.get_relative_transform().rotation.rotator().yaw)<.001
 assert not a.service_key.is_visible() and not a.key_inspection_light.is_visible()
for name in ['runtime','safety']:
 r=json.loads((dest/(name+'.json')).read_text());assert r['success'] and all(r['checks'].values())
for name in ['review','headers']:
 r=json.loads((dest/(name+'.json')).read_text());assert r['error'] is None and r['temporary_lights_removed']
 assert all(Path(v['path']).is_file() for v in r['views'])
assert ls.save_current_level()
base=json.loads((OUT/'before.json').read_text())
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
assert hashlib.sha256((REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend').read_bytes()).hexdigest()=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
RESULT={'saved_closed':True,'actors':len(actors),'temporary_lights':0,'runtime_and_safety_passed':True,'original_map_unchanged':True,'blender_master_unchanged':True}
(dest/'final.json').write_text(json.dumps(RESULT,indent=2))
