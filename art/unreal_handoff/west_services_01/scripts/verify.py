"""Reopen installed content and check exact manifest ownership, baseline preservation and foliage persistence."""
import unreal,json,hashlib,math,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];B=json.loads((P/'baseline.json').read_text());D=json.loads((P/'exports.json').read_text());ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration';assert ls.save_current_level()
if JOB.get('reopen'):
 assert ls.load_level('/Engine/Maps/Entry');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};errors=[];allowed={'VF10_Parking_Terrain'}|{r['actor'] for r in json.loads((P/'deck_patch_install.json').read_text())};o=B['origin']
if (P/'janitor_patch_install.json').exists():allowed|={r['actor'] for r in json.loads((P/'janitor_patch_install.json').read_text())}
for r in B['actors']:
 if r['class']=='PlayerStart' and (P/'entry_acoustics.json').exists():r={**r,**json.loads((P/'entry_acoustics.json').read_text())['player_start']}
 a=by.get(r['label'])
 if not a:errors.append([r['label'],'missing baseline actor']);continue
 pos=a.get_actor_location();rot=a.get_actor_rotation();scale=a.get_actor_scale3d()
 for label,actual,expected in [('position',[pos.x,pos.y,pos.z],r['position']),('rotation',[rot.pitch,rot.yaw,rot.roll],r['rotation']),('scale',[scale.x,scale.y,scale.z],r['scale'])]:
  if max(abs(x-y) for x,y in zip(actual,expected))>.01:errors.append([r['label'],label])
 if r['label'] not in allowed:
  cs={c.get_name():c.static_mesh.get_path_name() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh}
  for c in r['meshes']:
   # Landscape grass components are transient, regenerated with the current viewport.
   if c['component'].startswith('GrassInstancedStaticMeshComponent'):continue
   if cs.get(c['component'])!=c['mesh']:errors.append([r['label'],c['component'],'mesh changed'])
for r in D['assets']:
 label='MIG_WS_'+__import__('re').sub('[^A-Za-z0-9_]','_',r['key']);a=by.get(label)
 if not a:errors.append([label,'missing import']);continue
 M=r['matrix'];expected=[o[0]-100*M[0][3],o[1]+100*M[1][3],o[2]+100*M[2][3]];p=a.get_actor_location()
 if max(abs(x-y) for x,y in zip([p.x,p.y,p.z],expected))>.02:errors.append([label,'placement'])
 c=a.moving_mesh if r['control'] else a.static_mesh_component
 if not c.static_mesh or c.static_mesh.get_name()!=r['mesh']:errors.append([label,'mesh'])
 if r['control'] and a.get_open_fraction()!=0:errors.append([label,'not closed'])
 if len(c.static_mesh.static_materials)!=len(r['materials']):errors.append([label,'slots'])
fol=by['InstancedFoliageActor0'];native=dict(unreal.StationMigrationLibrary.get_foliage_instance_transforms(fol));expected=json.loads((P/'native_foliage_baseline.json').read_text())
for row in json.loads((P/'site_install.json').read_text())['moves']+json.loads((P/'foliage_clearance_repair.json').read_text()):expected[row['key']]=row['after']
if set(expected)!=set(native):errors.append(['foliage','instance identity changed'])
for k,xyz in expected.items():
 if k not in native or (native[k].translation-unreal.Vector(*xyz)).length()>.1:errors.append(['foliage',k])
report={'errors':errors,'retained_actors':len(B['actors']),'imported_groups':len(D['assets']),'native_foliage_instances':len(native),'source_hash_matches':hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['source_sha256'],'r12_hash_matches':hashlib.sha256((R/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==B['r12_sha256'],'reopened':bool(JOB.get('reopen'))};report['passed']=not errors and report['source_hash_matches'] and report['r12_hash_matches'];(P/'verification.json').write_text(json.dumps(report,indent=2));RESULT=report
