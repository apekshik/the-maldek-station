import unreal,json,hashlib,itertools,math,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'doors';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
by={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();base=json.loads((OUT/'before.json').read_text());o=base['origin'];data=json.loads((dest/'exports.json').read_text());assets={r['name']:r for r in data['assets']};errors=[]
def xyz(p):return [p.x,p.y,p.z]
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
def mul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
before=json.loads((dest/'before.json').read_text())
for r in before:
 a=by[r['label']];rot=a.get_actor_rotation();assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))<.1
 assert max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))<.001
 assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))<.001
assert len([n for n in by if n.startswith('MIG_PLD_')])==3
names={'Leaf':'leaf','Glass':'glass','FixedHardware':'fixed_hardware','KeyHousing':'key_housing','KeyPlug':'key_plug','InteriorKeyPlug':'interior_key_plug','FrontLever':'front_lever','BackLever':'back_lever','MovingLatch':'moving_latch','BottomSeal':'bottom_seal'};mats=[];blocking=[]
for row in data['doors']:
 a=by['MIG_PLD_'+row['id']];assert a.is_locked() and a.key_available and a.use_authored_hardware and not a.has_keypad;assert abs(a.get_open_angle())<.001;assert not a.service_key.is_visible();assert a.get_editor_property('key_turn_volume')==4;assert a.key_turn_sound and a.close_sound and a.movement_sound
 for part in row['parts']:
  c=getattr(a,names[part['role']]);assert c.static_mesh.get_name()==part['mesh'];b=assets[part['mesh']];M=mul(row['hinge_matrix'],part['local_matrix']);points=[]
  for q in itertools.product(*zip(b['lo'],b['hi'])):points.append(xyz(wp([sum(M[j][k]*q[k] for k in range(3))+M[j][3] for j in range(3)])))
  expected=[[min(p[j] for p in points) for j in range(3)],[max(p[j] for p in points) for j in range(3)]];center,extent,_=unreal.SystemLibrary.get_component_bounds(c);actual=[xyz(center-extent),xyz(center+extent)];err=max(abs(x-y) for v,e in zip(actual,expected) for x,y in zip(v,e));assert err<.2,(row['id'],part['role'],err);errors.append(err)
  if c.get_material(0) not in mats:mats.append(c.get_material(0))
 for side in [-1,1]:
  t=a.get_actor_transform();start=unreal.MathLibrary.transform_location(t,unreal.Vector(row['width']*50+6,side*80,120));end=unreal.MathLibrary.transform_location(t,unreal.Vector(row['width']*50+6,-side*80,120));h=unreal.SystemLibrary.line_trace_single(w,start,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True);assert h and h.to_tuple()[0] and h.to_tuple()[9]==a;blocking.append(a.get_actor_label())
shaders=list(unreal.StationMigrationLibrary.validate_material_shaders(mats));assert not shaders
samples=[]
try:
 for row in data['doors']:by['MIG_PLD_'+row['id']].hinge.set_relative_rotation(unreal.Rotator(pitch=0,yaw=row['open_angle'],roll=0),False,False)
 paths={'MainHall':[[-17.1,-6.4,4],[-17.1,5.5,4]],'CrossAisleNorth':[[-22,1,4],[-11,1,4]],'CrossAisleSouth':[[-22,-2.3,4],[-11,-2.3,4]],'CoffeeApproach':[[-17.1,-5.7,4],[-21.5,-5.7,4]],'Staff':[[-17.5,-10.5,4],[-20,-10.5,4]]}
 for name,path in paths.items():
  for a,b in zip(path,path[1:]):
   for i in range((n:=max(1,math.ceil(math.dist(a,b)/.2)))+1):
    p=[x+(y-x)*i/n for x,y in zip(a,b)];c=wp([p[0],p[1],4.99]);h=unreal.SystemLibrary.capsule_trace_single(w,c,c+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);hit=h.to_tuple() if h else None;samples.append({'route':name,'point':p,'blocked':bool(hit and hit[0]),'actor':hit[9].get_actor_label() if hit and hit[0] and hit[9] else None})
 perimeter=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT']
finally:
 for row in data['doors']:by['MIG_PLD_'+row['id']].hinge.set_relative_rotation(unreal.Rotator(),False,False)
assert ls.save_current_level();original=hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256'];assert original
RESULT={'reopened':True,'preserved_actors':len(before),'doors':3,'components':len(errors),'max_component_bounds_error_cm':max(errors),'closed_leaf_traces':len(blocking),'shader_errors':shaders,'route_conditions':'New doors temporarily posed fully open; restored closed before saving','interior_samples':len(samples),'interior_failures':[r for r in samples if r['blocked']],'perimeter':perimeter,'original_map_unchanged':original}
(dest/'verification.json').write_text(json.dumps(RESULT,indent=2));assert not RESULT['interior_failures'],RESULT['interior_failures'];assert not perimeter['failures'],perimeter['failures']
