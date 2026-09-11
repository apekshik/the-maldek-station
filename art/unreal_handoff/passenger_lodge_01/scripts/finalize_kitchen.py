import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'kitchen';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();assert len(actors)==1200
assert not any(a.get_actor_label().startswith('Lodge_Surface_Review_Temporary') for a in actors)
controls=[a for a in actors if isinstance(a,unreal.StationCabinet)];assert len(controls)==15 and all(a.get_open_fraction()==0 for a in controls)
for a in controls:a.set_editor_property('display_name','drawer' if a.sliding else 'fridge' if '_Fridge_' in a.get_actor_label() else 'microwave' if '_Microwave_' in a.get_actor_label() else 'cupboard')
for name in ['runtime','safety']:
 r=json.loads((dest/(name+'.json')).read_text());assert r['success'] and all(r['checks'].values())
 if name=='runtime':assert len(r['routes'])==6 and len(r['images'])==21 and all(Path(p).is_file() for p in r['images'])
r=json.loads((dest/'review.json').read_text());assert not r['error'] and r['temporary_lights_removed'] and len(r['views'])==12;assert all(Path(v['path']).is_file() for v in r['views'])
v=json.loads((dest/'verification.json').read_text());assert v['reopened'] and v['previous_actors_preserved']==1175 and v['collision_boxes']==76 and not v['route_failures']
assert ls.save_current_level();base=json.loads((OUT/'before.json').read_text())
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
assert hashlib.sha256((REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend').read_bytes()).hexdigest()=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
RESULT={'saved_closed':True,'mechanisms':15,'actors':1200,'temporary_lights':0,'tests_passed':True,'original_map_unchanged':True,'blender_master_unchanged':True};(dest/'final.json').write_text(json.dumps(RESULT,indent=2))
