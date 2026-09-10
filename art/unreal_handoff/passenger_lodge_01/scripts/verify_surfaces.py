import unreal,json,re,hashlib,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
if JOB.get('reopen'):
 assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};base=json.loads((OUT/'before.json').read_text());o=base['origin'];errors=[]
def xyz(p):return [p.x,p.y,p.z]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for r in json.loads((OUT/'windows/before.json').read_text()):
 a=by.get(r['label']);assert a,r['label'];rot=a.get_actor_rotation()
 if max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))>.1:errors.append('Position '+r['label'])
 if max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))>.001:errors.append('Rotation '+r['label'])
 if max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))>.001:errors.append('Scale '+r['label'])
assert not any('Surface_Review_Temporary' in n for n in by),'Review light leaked'
data=json.loads((OUT/'windows/exports.json').read_text());assets={r['name']:r for r in data['assets']}
assert len([n for n in by if n.startswith('MIG_PLW_')])==len(data['placements'])
bounds_errors=[]
for r in data['placements']:
 a=by[r['label']];p=wp(r['pivot']);assert (a.get_actor_location()-p).length()<.1
 b=assets[r['mesh']];c,e=a.get_actor_bounds(False);lo,hi=xyz(c-e),xyz(c+e);pivot=r['pivot']
 expected_lo=xyz(wp([pivot[0]+b['hi'][0],pivot[1]+b['lo'][1],pivot[2]+b['lo'][2]]));expected_hi=xyz(wp([pivot[0]+b['lo'][0],pivot[1]+b['hi'][1],pivot[2]+b['hi'][2]]))
 err=max(abs(x-y) for actual,want in zip([lo,hi],[expected_lo,expected_hi]) for x,y in zip(actual,want));assert err<.2,(r['label'],err);bounds_errors.append(err)
 assert a.static_mesh_component.static_mesh.get_name()==r['mesh']
 assert str(a.static_mesh_component.get_collision_profile_name())=='BlockAll'
for kind in ['Shell','Deck']:
 for r in json.loads((OUT/(kind.lower()+'_exports.json')).read_text())['assets']:
  mesh=lib.load_asset('/Game/MaldekRefinement/PassengerLodge/'+kind+'Pilot/Meshes/'+r['name']);assert mesh
  for i,name in enumerate(r['materials']):assert mesh.get_material(i).get_name()=='M_'+re.sub(r'[^a-zA-Z0-9_]','_',name)
mats=[lib.load_asset(r['asset']) for r in json.loads((OUT/'surface_materials.json').read_text())['materials']];shader_errors=list(unreal.StationMigrationLibrary.validate_material_shaders(mats));assert not shader_errors,shader_errors
traces=[];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for start in [-22.7,-15.5]:
 for dx in [.5,1.9,3.3]:
  for direction in [-1,1]:
   h=unreal.SystemLibrary.line_trace_single(w,wp([start+dx,4+direction,5.65]),wp([start+dx,4-direction,5.65]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
   assert h and h.to_tuple()[0];label=h.to_tuple()[9].get_actor_label();assert label.startswith('MIG_PLW_'),label;traces.append(label)
routes=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT'];assert not routes['failures']
original=hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256'];assert original
assert not errors,errors
RESULT={'reopened':bool(JOB.get('reopen')),'errors':errors,'window_assemblies':2,'window_actors':len(data['placements']),'window_max_bounds_error_cm':max(bounds_errors),'pane_traces_both_sides':len(traces),'surface_materials':len(mats),'shader_errors':shader_errors,'route_samples':routes['samples'],'route_failures':routes['failures'],'original_map_unchanged':original}
(OUT/'surface_verification.json').write_text(json.dumps(RESULT,indent=2))
