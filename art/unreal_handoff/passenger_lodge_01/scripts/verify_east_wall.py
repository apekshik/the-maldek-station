"""Reopen the complete furnished migration, check dependencies and circulation."""
import unreal,json,hashlib,itertools,math,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'east_wall';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();by={a.get_actor_label():a for a in aa.get_all_level_actors()};base=json.loads((OUT/'before.json').read_text());o=base['origin'];previous=json.loads((OUT/'east_wall/before.json').read_text())
def xyz(v):return [v.x,v.y,v.z]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for r in previous:
 a=by[r['label']];rot=a.get_actor_rotation();assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))<.1;assert max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))<.001;assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))<.001
added=json.loads((dest/'install.json').read_text())['actors'];assert len(previous)==1248 and len(by)==len(previous)+len(added)
errors=[];materials=[];textures=[];boxes=0
for package,folder,prefix in [('lockers','Lockers','PLL'),('wall_displays','WallDisplays','PLG'),('east_wall','EastWall','PLG2')]:
 data=json.loads((OUT/package/'exports.json').read_text());assets={a['name']:a for a in data['assets']};root='/Game/MaldekRefinement/PassengerLodge/'+folder
 for row in data['groups']:
  for channel,t in row['textures'].items():
   assert hashlib.sha256((OUT/package/t['file']).read_bytes()).hexdigest()==t['sha256'];tex=unreal.EditorAssetLibrary.load_asset(root+'/Textures/T_'+prefix+'_'+row['id']+'_'+channel);assert tex and tex.get_editor_property('srgb')==(channel=='BaseColor');textures.append(tex.get_path_name())
   if channel=='NormalGL':assert tex.get_editor_property('flip_green_channel')
  if package=='lockers':
   a=by['MIG_PLL_'+row['id']];assert a.get_open_fraction()==0 and a.get_cam_release()==0;bs=[c for c in a.get_components_by_class(unreal.BoxComponent) if 'KitchenMovingCollision' in [str(t) for t in c.component_tags]];assert len(bs)==5;boxes+=len(bs)
  for part in row['parts']:
   if package=='lockers':c=by['MIG_PLL_'+row['id']+'_Body'].static_mesh_component if part['role']=='Static' else a.moving_mesh if part['role']=='Leaf' else a.cam
   elif package=='east_wall':c=by['MIG_PLG2_FirstAid'].moving_mesh if part['role']=='Leaf' else by['MIG_PLG2_'+part['role']].static_mesh_component
   else:c=by['MIG_PLG_'+part['role']].static_mesh_component
   assert c.static_mesh.get_name()==part['mesh'];b=assets[part['mesh']];M=part['matrix'];pts=[]
   for q in itertools.product(*zip(b['lo'],b['hi'])):pts.append(xyz(wp([sum(M[j][k]*q[k] for k in range(3))+M[j][3] for j in range(3)])))
   low=[min(p[j] for p in pts) for j in range(3)];high=[max(p[j] for p in pts) for j in range(3)];center,extent,_=unreal.SystemLibrary.get_component_bounds(c);err=max(abs(x-y) for got,expected in zip([xyz(center-extent),xyz(center+extent)],[low,high]) for x,y in zip(got,expected));assert err<.2,(package,part['role'],err);errors.append(err)
   for i in range(c.get_num_materials()):
    mat=c.get_material(i);assert mat
    if mat not in materials:materials.append(mat)
 for name,t in data.get('printed_materials',{}).items():
  assert hashlib.sha256((OUT/package/t['file']).read_bytes()).hexdigest()==t['sha256'];tex=unreal.EditorAssetLibrary.load_asset(root+'/Textures/T_'+name);assert tex and tex.get_editor_property('srgb');textures.append(tex.get_path_name())
assert not list(unreal.StationMigrationLibrary.validate_material_shaders(materials))
routes={r['name']:r['path_local'] for r in json.loads((REPO/'art/blender/passenger_lodge_restrooms_01/verification.json').read_text())['routes']}
routes.update(json.loads((OUT/'kitchen/routes.json').read_text()));routes.update({'Main_hall':[(7,10.4),(7,.5)],'Lockers':[(7,9.8),(11.7,9.8),(13.1,9.8)],'Coffee_public':[(7,9.7),(2.6,9.7),(2.6,9.9)]})
routes.update({k:v for k,v in json.loads((REPO/'art/blender/passenger_lodge_wall_details_02/routes_input.json').read_text()).items() if k.startswith('East') or k=='First_aid_approach'})
(dest/'routes.json').write_text(json.dumps(routes,indent=2));samples=[];floor=[];poses=[]
try:
 for a in by.values():
  if a.get_actor_label().startswith(('MIG_PLR_','MIG_PLD_')) and isinstance(a,unreal.StationDoor):poses.append(a.hinge);a.hinge.set_relative_rotation(unreal.Rotator(yaw=a.open_angle),False,False)
  if a.get_actor_label().startswith('MIG_PLL_') and isinstance(a,unreal.StationCabinet):poses.append(a.pivot);a.pivot.set_relative_rotation(unreal.Rotator(yaw=-100),False,False)
 firstaid=by['MIG_PLG2_FirstAid'];poses.append(firstaid.pivot);firstaid.pivot.set_relative_rotation(unreal.Rotator(yaw=95),False,False)
 for name,points in routes.items():
  for a,b in zip(points,points[1:]):
   for i in range((n:=max(1,math.ceil(math.dist(a,b)/.05)))+1):
    p=[a[j]+(b[j]-a[j])*i/n for j in range(2)];c=wp([p[0]-24.1,4-p[1],4.99]);hit=unreal.SystemLibrary.capsule_trace_single(w,c,c+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;samples.append({'route':name,'point':p,'blocked':bool(h and h[0]),'actor':h[9].get_actor_label() if h and h[0] and h[9] else None})
  for p in points:
   c=wp([p[0]-24.1,4-p[1],4.1]);hit=unreal.SystemLibrary.line_trace_single(w,c,c-unreal.Vector(0,0,25),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None;floor.append({'route':name,'supported':bool(h and h[0])})
 perimeter=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT']
finally:
 for c in poses:c.set_relative_rotation(unreal.Rotator(),False,False)
assert all(a.get_open_fraction()==0 and a.get_cam_release()==0 for a in by.values() if isinstance(a,unreal.StationCabinet))
assert not any(a.get_actor_label().startswith(('Lodge_Surface_Review_Temporary','TEMP_Audio')) for a in by.values())
assert by['MIG_PLD_GONDOLA'].key_camera_offset.x==-18
assert by['MIG_Lodge_Sheltered_Storm'].wind_loop and by['MIG_Lodge_Sheltered_Storm'].weather_actor
assert len(by['MIG_PLG2_FirstAid'].opening_takes)==2
assert len([a for a in by.values() if a.get_actor_label().startswith('MIG_PLL_') and isinstance(a,unreal.StationCabinet)])==12
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'reopened':True,'previous_actors_preserved':len(previous),'actors':len(by),'components':len(errors),'textures_verified':len(textures),'maximum_bounds_error_cm':max(errors),'lockers':12,'locker_collision_boxes':boxes,'route_count':len(routes),'route_samples':len(samples),'route_failures':[s for s in samples if s['blocked']],'unsupported':[r for r in floor if not r['supported']],'perimeter':perimeter,'source_map_unchanged':True,'poses_restored_closed':True}
(dest/'verification.json').write_text(json.dumps(RESULT,indent=2));assert not RESULT['route_failures'],RESULT['route_failures'];assert not RESULT['unsupported'];assert not perimeter['failures']
