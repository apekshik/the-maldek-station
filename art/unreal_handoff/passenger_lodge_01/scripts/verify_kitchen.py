"""Reopen, reconcile component fit, openings and fixture access at player scale."""
import unreal,json,hashlib,itertools,math,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'kitchen';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();by={a.get_actor_label():a for a in aa.get_all_level_actors()};data=json.loads((dest/'exports.json').read_text());assets={a['name']:a for a in data['assets']};base=json.loads((OUT/'before.json').read_text());o=base['origin'];previous=json.loads((dest/'before.json').read_text())
def xyz(v):return [v.x,v.y,v.z]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for r in previous:
 a=by[r['label']];rot=a.get_actor_rotation();assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))<.1;assert max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))<.001;assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))<.001
errors=[];materials=[];textures=[];mechanisms=0;boxes=0
for row in data['groups']:
 for channel,t in row['textures'].items():
  assert hashlib.sha256((dest/t['file']).read_bytes()).hexdigest()==t['sha256'];path='/Game/MaldekRefinement/PassengerLodge/Kitchen/Textures/T_PLK_'+row['id']+'_'+channel;tex=unreal.EditorAssetLibrary.load_asset(path);assert tex and tex.get_editor_property('srgb')==(channel=='BaseColor')
  if channel=='NormalGL':assert tex.get_editor_property('flip_green_channel')
  textures.append(path)
 for part in row['parts']:
  label='MIG_PLK_'+row['id']+'_'+part['role'];a=by[label];c=a.moving_mesh if part['control'] else a.static_mesh_component
  assert c.static_mesh.get_name()==part['mesh'];b=assets[part['mesh']];M=part['matrix'];pts=[]
  for q in itertools.product(*zip(b['lo'],b['hi'])):pts.append(xyz(wp([sum(M[j][k]*q[k] for k in range(3))+M[j][3] for j in range(3)])))
  low=[min(p[j] for p in pts) for j in range(3)];high=[max(p[j] for p in pts) for j in range(3)];center,extent,_=unreal.SystemLibrary.get_component_bounds(c);err=max(abs(x-y) for got,expected in zip([xyz(center-extent),xyz(center+extent)],[low,high]) for x,y in zip(got,expected));assert err<.2,(label,err);errors.append(err)
  if part['control']:
   assert a.get_open_fraction()==0;bs=[c for c in a.get_components_by_class(unreal.BoxComponent) if 'KitchenMovingCollision' in [str(t) for t in c.component_tags]];assert len(bs)==len(part['collision']),(label,len(bs));boxes+=len(bs);mechanisms+=1
  if c.get_material(0) not in materials:materials.append(c.get_material(0))
assert not list(unreal.StationMigrationLibrary.validate_material_shaders(materials))
routes={'staff_entry':[(5.7,14.5),(4.60,14.5)],'door_to_counter':[(4.60,14.5),(3.5,14.5),(2.1,14.5),(2.1,12.05)],'wash_approach':[(2.1,14.5),(1.36,14.58)],'handwash_approach':[(3.5,14.5),(3.55,13.24),(3.84,13.24)],'rear_prep':[(3.5,14.5),(3.5,14.90)],'fridge':[(2.1,14.5),(2.58,14.87)]}
(dest/'routes.json').write_text(json.dumps(routes,indent=2));samples=[];floor=[];poses=[]
try:
 for a in by.values():
  if a.get_actor_label().startswith(('MIG_PLR_','MIG_PLD_')) and isinstance(a,unreal.StationDoor):poses.append(a);a.hinge.set_relative_rotation(unreal.Rotator(yaw=a.open_angle),False,False)
 for name,points in routes.items():
  for a,b in zip(points,points[1:]):
   for i in range((n:=max(1,math.ceil(math.dist(a,b)/.05)))+1):
    p=[a[j]+(b[j]-a[j])*i/n for j in range(2)];c=wp([p[0]-24.1,4-p[1],4.99]);hit=unreal.SystemLibrary.capsule_trace_single(w,c,c+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;samples.append({'route':name,'point':p,'blocked':bool(h and h[0]),'actor':h[9].get_actor_label() if h and h[0] and h[9] else None})
  for p in points:
   c=wp([p[0]-24.1,4-p[1],4.1]);hit=unreal.SystemLibrary.line_trace_single(w,c,c-unreal.Vector(0,0,25),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;floor.append({'route':name,'supported':bool(h and h[0])})
 perimeter=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT']
finally:
 for a in poses:a.hinge.set_relative_rotation(unreal.Rotator(),False,False)
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'reopened':True,'previous_actors_preserved':len(previous),'actors':len(by),'components':len(errors),'textures_verified':len(textures),'maximum_bounds_error_cm':max(errors),'mechanisms':mechanisms,'collision_boxes':boxes,'route_samples':len(samples),'route_failures':[s for s in samples if s['blocked']],'unsupported':[r for r in floor if not r['supported']],'perimeter':perimeter,'source_map_unchanged':True,'poses_restored_closed':True}
(dest/'verification.json').write_text(json.dumps(RESULT,indent=2));assert not RESULT['route_failures'],RESULT['route_failures'];assert not RESULT['unsupported'];assert not perimeter['failures']
