import unreal,json,re
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'platform_refine'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
installation=json.loads((out/'installation.json').read_text());removed={r['label'] for r in installation['removed']};errors=[]
preserve=json.loads((out/'preserve.json').read_text())
for label,t in preserve.items():
 if label in removed:
  if label in actors:errors.append('Removed canopy part remains: '+label)
 elif label not in actors or re.sub(r'\(0x[0-9A-Fa-f]+\)','',str(actors[label].get_actor_transform()))!=t:errors.append('Unexpected actor change: '+label)
for r in installation['markers']:
 if not r['rail_hit']:errors.append('Unsupported marker: '+r['name'])
 for part in ['Base','Lens']:
  a=actors.get('R12_EdgeMarker_'+r['name']+'_'+part)
  if not a or a.static_mesh_component.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:errors.append('Marker missing or blocking: '+r['name']+part)
 c=actors['R12_EdgeMarker_'+r['name']+'_Spill'].point_light_component
 if abs(c.intensity-.045)>.00001 or c.attenuation_radius!=90:errors.append('Marker spill mismatch')
sky=actors['Ultra_Dynamic_Sky'];night=json.loads((b/'gorge'/'night_sky_settings.json').read_text())
for k,v in night.items():
 if sky.get_editor_property(k)!=v:errors.append('Night sky changed: '+k)
assert ls.save_current_level();RESULT={'passed':not errors,'errors':errors,'removed_canopy_actors':len(removed),'marker_count':len(installation['markers']),'preserved_actors':len(preserve)-len(removed),'night_restored':not any('Night sky' in e for e in errors)}
(out/'verification.json').write_text(json.dumps(RESULT,indent=2))
