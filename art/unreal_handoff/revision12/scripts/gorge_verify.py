"""Check ground collision and unchanged building/lighting actor transforms."""
import unreal,json,re
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];grid={(round(x,3),round(y,3)):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def wp(x,y,z):return unreal.Vector(o[0]-x*100,o[1]+y*100,o[2]+z*100)
preserve=json.loads((out/'preserve_resume.json').read_text());moved=json.loads((out/'dressing.json').read_text())['result']['existing_actors_grounded'];errors=[]
density=json.loads((out/'density'/'installation.json').read_text()) if (out/'density'/'installation.json').exists() else {'added':0,'removed':[]}
removed={r['label'] for r in density['removed']}
if (b/'platform_refine'/'installation.json').exists():removed.update(r['label'] for r in json.loads((b/'platform_refine'/'installation.json').read_text())['removed'])
for label,t in preserve.items():
 if label in removed:
  if label in actors:errors.append('Removed actor still present: '+label)
  continue
 if label in moved:continue
 def stable(s):return re.sub(r'\(0x[0-9A-Fa-f]+\)','',s)
 if label not in actors or stable(str(actors[label].get_actor_transform()))!=stable(t):errors.append('Actor changed: '+label)
ground=[a for a in actors.values() if isinstance(a,unreal.Landscape) or a.get_actor_label()=='VF10_Parking_Terrain'];ignore=[a for a in actors.values() if a not in ground];checks=[]
for x,y in [(-7,7),(-7,12),(-7,20),(-7,30),(-7,40),(-7,60),(-7,90),(-30,-35),(-10,-27),(30,-15),(-16,-5),(2,3),(-14,-17)]:
 hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,40),wp(x,y,-240),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 if not hit:errors.append('No collision '+str((x,y)));continue
 z=(hit.to_tuple()[5].z-o[2])/100;err=abs(z-grid[x,y]);checks.append({'xy':[x,y],'ground_m':z,'expected':grid[x,y],'error_m':err})
 if err>.06:errors.append('Terrain collision mismatch '+str((x,y)))
native=json.loads((out/('native_edge_patch.json' if (out/'native_edge_applied.json').exists() else 'native_probe.json')).read_text());land=next(a for a in actors.values() if isinstance(a,unreal.Landscape))
actual=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*native['bounds'],-1))
native_errors=sum(abs(a-b)>1 for a,b in zip(actual,native['expected_merged']))
if native_errors:errors.append('Merged native height mismatches: '+str(native_errors))
night=json.loads((out/'night_sky_settings.json').read_text());sky=actors['Ultra_Dynamic_Sky'];sky_after={k:sky.get_editor_property(k) for k in night}
for k,v in night.items():
 if isinstance(v,bool):same=sky_after[k]==v
 else:same=abs(sky_after[k]-v)<.001
 if not same:errors.append('Night setting changed: '+k)
mesh=actors['VF10_Parking_Terrain'].static_mesh_component.static_mesh
if any('M_Gorge_Ground' not in str(s.material_interface) for s in mesh.get_editor_property('static_materials')):errors.append('Terrain material slot mismatch')
tree_count=0;root_errors=[]
for a in actors.values():
 if not isinstance(a,unreal.InstancedFoliageActor):continue
 for key,t in unreal.StationMigrationLibrary.get_foliage_instance_transforms(a).items():
  if '/R12/Gorge/Foliage/' not in key:continue
  tree_count+=1;x=(o[0]-t.translation.x)/100;y=(t.translation.y-o[1])/100
  hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,40),wp(x,y,-240),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  if not hit:root_errors.append(key);continue
  fm=unreal.load_asset(key.rsplit('|',1)[0]).get_editor_property('mesh');bd=fm.get_bounds();base=t.translation.z+(bd.origin.z-bd.box_extent.z)*t.scale3d.z;burial=hit.to_tuple()[5].z-base
  if not 5<=burial<=40:root_errors.append([key,burial])
if tree_count!=172+density['added'] or root_errors:errors.append('Gorge tree count/rooting mismatch')
assert ls.save_current_level();RESULT={'passed':not errors,'errors':errors,'collision':checks,'preserved_actor_count':len(set(preserve)-set(moved)-removed),'merged_height_readback_errors':native_errors,'sky_restored':sky_after,'new_tree_count':tree_count,'tree_root_errors':root_errors}
(out/'verification.json').write_text(json.dumps(RESULT,indent=2))
