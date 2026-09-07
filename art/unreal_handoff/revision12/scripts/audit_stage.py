"""Verify every imported placement/material/collision and every preserved actor identity."""
import unreal,json,re,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
ledger=json.loads((base/'integration_ledger.json').read_text());manifest=json.loads((base/'handoff_manifest.json').read_text());inventory=json.loads((base/'replacement_inventory.json').read_text())
actors={a.get_path_name():a for a in aa.get_all_level_actors()};origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
adjustments=json.loads((base/'actor_adjustments.json').read_text()) if (base/'actor_adjustments.json').exists() else {}
checks=[];errors=[]
for r in manifest['chunks']:
 if r['name'] not in ledger['assets']:continue
 l=ledger['assets'][r['name']];a=actors.get(l['actor'])
 if not a:errors.append('Missing '+r['name']);continue
 p=a.get_actor_location();wanted=[origin[0]-100*r['pivot'][0],origin[1]+100*r['pivot'][1],origin[2]+100*r['pivot'][2]]
 delta=max(abs(x-y) for x,y in zip([p.x,p.y,p.z],wanted));assert delta<.1,(r['name'],delta)
 assert abs(abs(a.get_actor_rotation().yaw)-180)<.01,r['name']
 c=a.static_mesh_component;assert c.static_mesh.get_path_name().split('.')[0]==l['asset'],r['name']
 assert not c.get_editor_property('override_materials'),r['name']
 assert all(c.get_material(i) for i in range(c.get_num_materials())),r['name']
 checks.append({'name':r['name'],'placement_error_cm':delta,'materials':c.get_num_materials(),'hulls':l['hulls']})
for r in inventory:
 assert r['r12_path'] in actors,('Lost original actor',r['r12_path'])
 actual=re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',str(actors[r['r12_path']].get_actor_transform()))
 expected=re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',adjustments.get(r['r12_path'],{}).get('new_transform',r['transform']))
 assert actual==expected,('Original actor transform changed',r['label'],actual,expected)
for key,t in ledger['retired'].items():
 a=actors[t['actor']];c=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()==t['component'])
 assert c.static_mesh is None and c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION,key
removed=[]
if JOB.get('remove_pilot'):
 for r in json.loads((base/'probe_import.json').read_text())['assets']:
  a=actors.get(r['actor'])
  if a:
   assert a.get_actor_label()==r['name'].replace('SM_',''),a.get_path_name()
   removed.append(a.get_path_name());assert aa.destroy_actor(a)
 assert levels.save_current_level()
report={'success':not errors,'stage':JOB.get('stage'),'assets':checks,'original_actor_identities_preserved':len(inventory),'retired_components':len(ledger['retired']),'pilot_actors_removed':removed,'errors':errors,'note':'Structural audit only. Runtime route and visual review are separate acceptance gates.'}
(base/('audit_'+JOB.get('stage','all').lower()+'.json')).write_text(json.dumps(report,indent=2));RESULT={k:v for k,v in report.items() if k!='assets'}
