"""Verify completed evidence and save the vacant, closed restroom checkpoint."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'restrooms';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();assert len(actors)==1175;assert not any(a.get_actor_label().startswith('Lodge_Surface_Review_Temporary') for a in actors)
doors=[a for a in actors if a.get_actor_label().startswith('MIG_PLR_') and isinstance(a,unreal.StationDoor)];assert len(doors)==5
for a in doors:
 assert not a.is_locked() and abs(a.hinge.get_relative_transform().rotation.rotator().yaw)<.001;assert not a.service_key.is_visible() and not a.key_inspection_light.is_visible()
for name in ['runtime','safety']:
 r=json.loads((dest/(name+'.json')).read_text());assert r['success'] and all(r['checks'].values())
 if name=='runtime':assert len(r['routes'])==9 and all(Path(p).is_file() for p in r['images'])
r=json.loads((dest/'review.json').read_text());assert not r['error'] and r['temporary_lights_removed'];assert len(r['views'])==26;assert all(Path(v['path']).is_file() for v in r['views'])
assert ls.save_current_level();base=json.loads((OUT/'before.json').read_text())
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
assert hashlib.sha256((REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend').read_bytes()).hexdigest()=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
RESULT={'saved_closed_and_vacant':True,'doors':len(doors),'actors':len(actors),'temporary_lights':0,'tests_passed':True,'original_map_unchanged':True,'blender_master_unchanged':True};(dest/'final.json').write_text(json.dumps(RESULT,indent=2))
