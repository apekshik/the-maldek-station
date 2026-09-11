"""Reopen, reconcile component fit, openings and fixture access at player scale."""
import unreal,json,hashlib,itertools,math,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'restrooms';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();by={a.get_actor_label():a for a in aa.get_all_level_actors()};data=json.loads((dest/'exports.json').read_text());assets={a['name']:a for a in data['assets']};base=json.loads((OUT/'before.json').read_text());o=base['origin'];previous=json.loads((dest/'before.json').read_text())
def xyz(v):return [v.x,v.y,v.z]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for r in previous:
 a=by[r['label']];rot=a.get_actor_rotation();assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))<.1;assert max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))<.001;assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))<.001
components={'Leaf':'leaf','FixedHardware':'fixed_hardware','FrontLever':'front_lever','BackLever':'back_lever','MovingLatch':'moving_latch','Indicator':'privacy_indicator'};errors=[];materials=[];traces=[];textures=[]
for row in data['groups']:
 label='MIG_PLR_'+row['id'];H=row['matrix']
 for channel,t in row['textures'].items():
  assert hashlib.sha256((dest/t['file']).read_bytes()).hexdigest()==t['sha256'];path='/Game/MaldekRefinement/PassengerLodge/Restrooms/Textures/T_PLR_'+row['id']+'_'+channel;tex=unreal.EditorAssetLibrary.load_asset(path);assert tex and tex.get_editor_property('srgb')==(channel=='BaseColor')
  if channel=='NormalGL':assert tex.get_editor_property('flip_green_channel') and tex.get_editor_property('compression_settings')==unreal.TextureCompressionSettings.TC_NORMALMAP
  textures.append(path)
 if row['door']:
  a=by[label];assert not a.is_locked() and abs(a.get_open_angle())<.001 and not a.has_key_lock and not a.has_keypad;assert a.has_privacy_latch==(not row['entry'])
  center=a.leaf_collision.get_relative_transform().translation
  for side in [-1,1]:
   start=unreal.MathLibrary.transform_location(a.get_actor_transform(),center+unreal.Vector(0,side*90,0));end=unreal.MathLibrary.transform_location(a.get_actor_transform(),center-unreal.Vector(0,side*90,0));h=unreal.SystemLibrary.line_trace_single(w,start,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True);assert h and h.to_tuple()[0] and h.to_tuple()[9]==a;traces.append(label)
 for part in row['parts']:
  c=by[label+'_Fixtures'].static_mesh_component if part['role']=='Static' else getattr(by[label],components[part['role']]);assert c.static_mesh.get_name()==part['mesh'];b=assets[part['mesh']];L=part['local_matrix'];M=[[sum(H[j][k]*L[k][i] for k in range(4)) for i in range(4)] for j in range(4)];pts=[]
  for q in itertools.product(*zip(b['lo'],b['hi'])):pts.append(xyz(wp([sum(M[j][k]*q[k] for k in range(3))+M[j][3] for j in range(3)])))
  low=[min(p[j] for p in pts) for j in range(3)];high=[max(p[j] for p in pts) for j in range(3)];center,extent,_=unreal.SystemLibrary.get_component_bounds(c);err=max(abs(x-y) for got,expected in zip([xyz(center-extent),xyz(center+extent)],[low,high]) for x,y in zip(got,expected));assert err<.2,(label,part['role'],err);errors.append(err)
  if c.get_material(0) not in materials:materials.append(c.get_material(0))
assert not list(unreal.StationMigrationLibrary.validate_material_shaders(materials))
source=json.loads((REPO/'art/blender/passenger_lodge_restrooms_01/verification.json').read_text());samples=[];floor=[];poses=[]
try:
 for a in by.values():
  if a.get_actor_label().startswith(('MIG_PLR_','MIG_PLD_')) and isinstance(a,unreal.StationDoor):poses.append(a);a.hinge.set_relative_rotation(unreal.Rotator(yaw=a.open_angle),False,False)
 for route in source['routes']:
  points=route['path_local']
  for a,b in zip(points,points[1:]):
   for i in range((n:=max(1,math.ceil(math.dist(a,b)/.05)))+1):
    p=[a[j]+(b[j]-a[j])*i/n for j in range(2)];c=wp([p[0]-24.1,4-p[1],4.99]);hit=unreal.SystemLibrary.capsule_trace_single(w,c,c+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;samples.append({'route':route['name'],'point':p,'blocked':bool(h and h[0]),'actor':h[9].get_actor_label() if h and h[0] and h[9] else None})
  for p in points:
   c=wp([p[0]-24.1,4-p[1],4.1]);hit=unreal.SystemLibrary.line_trace_single(w,c,c-unreal.Vector(0,0,25),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;floor.append({'route':route['name'],'supported':bool(h and h[0])})
 perimeter=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT']
finally:
 for a in poses:a.hinge.set_relative_rotation(unreal.Rotator(),False,False)
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'reopened':True,'previous_actors_preserved':len(previous),'actors':len(by),'components':len(errors),'textures_verified':len(textures),'maximum_bounds_error_cm':max(errors),'closed_door_traces':len(traces),'route_samples':len(samples),'route_failures':[s for s in samples if s['blocked']],'unsupported':[r for r in floor if not r['supported']],'perimeter':perimeter,'source_map_unchanged':True,'poses_restored_closed':True}
(dest/'verification.json').write_text(json.dumps(RESULT,indent=2));assert not RESULT['route_failures'],RESULT['route_failures'];assert not RESULT['unsupported'];assert not perimeter['failures']
