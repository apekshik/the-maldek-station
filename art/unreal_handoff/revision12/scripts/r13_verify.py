import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[2]/'revision13';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
before=json.loads((b/'live_before.json').read_text());ledger=json.loads((b/'integration_ledger.json').read_text());manifest=json.loads((b/'handoff_manifest.json').read_text());actors={a.get_path_name():a for a in aa.get_all_level_actors()};retired={(r['actor'],r['component']) for r in ledger['retired']};errors=[]
for r in before['actors']:
 a=actors.get(r['path'])
 if not a:errors.append(['missing_actor',r['path']]);continue
 if r['label']!='R12_Audio_Generator' and (a.get_actor_location()-unreal.Vector(*r['location'])).length()>.1:errors.append(['moved_actor',r['label']])
 cs={c.get_name():c for c in a.get_components_by_class(unreal.StaticMeshComponent)}
 for old in r['components']:
  c=cs.get(old['name']);actual=c.static_mesh.get_path_name() if c and c.static_mesh else None
  expected=None if (r['path'],old['name']) in retired else old['mesh']
  if actual!=expected:errors.append(['unexpected_mesh',r['label'],old['name'],actual,expected])
for r in manifest['chunks']:
 row=ledger['assets'][r['name']];a=actors.get(row['actor']);m=lib.load_asset(row['asset'])
 if not a or not m or a.static_mesh_component.static_mesh!=m:errors.append(['missing_import',r['name']]);continue
 for slot in m.static_materials:
  if not slot.material_interface:errors.append(['missing_material',r['name'],str(slot.material_slot_name)])
 if r['collision_hulls'] or r.get('complex_collision'):
  if a.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION:errors.append(['missing_collision',r['name']])
env=json.loads((b/'environment.json').read_text());moves={r['key']:r for r in json.loads((b/'foliage_moves.json').read_text())};o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
for r in env['foliage']:
 a=actors[r['actor']];trans=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a);t=trans.get(r['key']);p=moves.get(r['key'],{}).get('after');expected=unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100) if p else unreal.Vector(*r['world'])
 if not t or (t.translation-expected).length()>.1:errors.append(['foliage_mismatch',r['key']])
report={'success':not errors,'errors':errors,'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'imports':len(ledger['assets']),'preserved_original_actors':len(before['actors']),'retired_components':len(retired),'foliage_instances_checked':len(env['foliage']),'reopened':JOB.get('reopened',False)}
(b/'saved_verification.json').write_text(json.dumps(report,indent=2));assert report['success'],errors;RESULT=report
