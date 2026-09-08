"""Collision, placements and preservation checks on the live R12 map."""
import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
before=json.loads((out/'live_before.json').read_text());o=before['origin'];errors=[];preserved=0
retired=set(json.loads((out/'install.json').read_text())['retired_rock_patches'])
if (out/'rocks'/'placement.json').exists():retired.add('VF10_Parking_Rock_Clusters')
if (out/'vehicles'/'placement.json').exists():retired.update(r['label'] for r in json.loads((out/'vehicles'/'placement.json').read_text())['retired'])
rooted={r['label'] for r in json.loads((out/'rooting.json').read_text()).get('actor_moves',[])} if (out/'rooting.json').exists() else set()
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
for row in before['actors']:
 a=actors.get(row['label'])
 if not a:errors.append('Missing '+row['label']);continue
 if row['label'] not in rooted and max(abs(v-t) for v,t in zip(local(a.get_actor_location()),row['local']))>.001:errors.append('Moved '+row['label'])
 if row['label']!='VF10_Parking_Terrain' and row['label'] not in retired and not isinstance(a,(unreal.Landscape,unreal.InstancedFoliageActor)):
  paths=[c.static_mesh.get_path_name() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
  if paths!=[c['mesh'] for c in row['components']]:errors.append('Changed mesh '+row['label'])
 preserved+=1
g={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
terrain=actors['VF10_Parking_Terrain'];ignore=[a for a in actors.values() if a!=terrain];samples=[]
for x,y in [(-30,-35),(-10,-27),(5,-29),(-25,-12),(-7,12),(-7,20),(-7,35),(-20,35),(17,25),(30,40),(50,50)]:
 expected=g[x,y];hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,30),wp(x,y,-180),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 if not hit:errors.append(f'No terrain collision {x,y}');continue
 z=local(hit.to_tuple()[5])[2];err=abs(z-expected);samples.append({'xy':[x,y],'expected':expected,'actual':z,'error_m':err})
 if err>.025:errors.append(f'Terrain mismatch {x,y}: {err}')
plant=json.loads((out/'planting.json').read_text());placement=[]
for p in plant['plants']+plant['trees']:
 a=actors[p['label']];actual=local(a.get_actor_location());err=max(abs(v-t) for v,t in zip(actual,p['local']));placement.append(err)
 if err>.001:errors.append('Plant moved '+p['label'])
stats=[]
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
  if c.get_instance_count()>0 and c.static_mesh and '/MWLandscapeAutoMaterial/Meshes/' in c.static_mesh.get_path_name():stats.append({'mesh':c.static_mesh.get_path_name(),'count':c.get_instance_count(),'collision':str(c.get_collision_enabled())})
expected=sum(plant['foliage_counts'].values());actual=sum(r['count'] for r in stats)
if actual<expected:errors.append(f'Missing foliage {actual} < {expected}')
assert ls.save_current_level();report={'passed':not errors,'errors':errors,'preserved_actors':preserved,'terrain_collision_samples':samples,'plant_placements':len(placement),'foliage':stats,'expected_foliage_instances':expected,'saved':True};(out/'verification.json').write_text(json.dumps(report,indent=2));RESULT={k:v for k,v in report.items() if k not in ['foliage','terrain_collision_samples']}
