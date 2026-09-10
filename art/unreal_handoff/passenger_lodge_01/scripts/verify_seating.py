import unreal,json,hashlib,math,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'seating';root='/Game/MaldekRefinement/PassengerLodge/Seating';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
if JOB.get('reopen'):
 assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();base=json.loads((OUT/'before.json').read_text());o=base['origin'];data=json.loads((dest/'exports.json').read_text())
def xyz(p):return [p.x,p.y,p.z]
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
before=json.loads((dest/'before.json').read_text())
for r in before:
 a=by[r['label']];rot=a.get_actor_rotation();assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_location()),r['position']))<.1
 assert max(abs((x-y+180)%360-180) for x,y in zip([rot.pitch,rot.yaw,rot.roll],r['rotation']))<.001
 assert max(abs(x-y) for x,y in zip(xyz(a.get_actor_scale3d()),r['scale']))<.001
assert len([n for n in by if n.startswith('MIG_PLS_')])==6
assets={a['name']:a for a in data['assets']};errors=[];mats=[];heights=[]
for index,r in enumerate(data['placements'],1):
 a=by[r['label']];c=a.static_mesh_component;assert c.static_mesh.get_name()==r['mesh'];assert str(c.get_collision_profile_name())=='BlockAll';assert c.get_material(0).get_name()=='M_PLS_%02d'%index;mats.append(c.get_material(0));p=r['pivot'];assert (a.get_actor_location()-wp(p)).length()<.1
 b=assets[r['mesh']];center,extent=a.get_actor_bounds(False);expected=[wp([p[0]+b['hi'][0],p[1]+b['lo'][1],p[2]+b['lo'][2]]),wp([p[0]+b['lo'][0],p[1]+b['hi'][1],p[2]+b['hi'][2]])]
 err=max(abs(x-y) for q,e in zip([center-extent,center+extent],expected) for x,y in zip(xyz(q),xyz(e)));assert err<.2;errors.append(err)
 for offset,z in [(0,.78),(-.775,.48),(.775,.48)]:
  # Offset along a plank to avoid intentional board gaps.
  point=[p[0]+.2,p[1]+offset+.04,p[2]];h=unreal.SystemLibrary.line_trace_single(w,wp([point[0],point[1],5.1]),wp([point[0],point[1],4.1]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
  assert h and h.to_tuple()[0];hit=h.to_tuple();assert hit[9]==a;actual=(hit[5].z-o[2])/100;assert abs(actual-4-z)<.005,(r['label'],actual,z);heights.append(actual)
 for channel in ['BaseColor','ORM','NormalGL']:
  tex=lib.load_asset(root+'/Textures/T_PLS_%02d_%s'%(index,channel));assert tex;assert tex.get_editor_property('srgb')==(channel=='BaseColor')
  if channel=='NormalGL':assert tex.get_editor_property('flip_green_channel')
shaders=list(unreal.StationMigrationLibrary.validate_material_shaders(mats));assert not shaders
paths={'MainHall':[[-17.1,-6.4,4],[-17.1,5.5,4]],'CrossAisleNorth':[[-22,1,4],[-11,1,4]],'CrossAisleSouth':[[-22,-2.3,4],[-11,-2.3,4]],'CoffeeApproach':[[-17.1,-5.7,4],[-21.5,-5.7,4]],'RestroomApproach':[[-17.1,-6.4,4],[-15.3,-6.4,4],[-15.3,-8.5,4]]};rows=[]
for name,path in paths.items():
 for a,b in zip(path,path[1:]):
  for i in range((n:=max(1,math.ceil(math.dist(a,b)/.2)))+1):
   p=[x+(y-x)*i/n for x,y in zip(a,b)];center=wp([p[0],p[1],p[2]+.99]);h=unreal.SystemLibrary.capsule_trace_single(w,center,center+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);t=h.to_tuple() if h else None
   f=unreal.SystemLibrary.sphere_trace_single(w,wp([p[0],p[1],4.15]),wp([p[0],p[1],3.7]),10,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
   rows.append({'route':name,'point':p,'blocked':bool(t and t[0]),'actor':t[9].get_actor_label() if t and t[0] and t[9] else None,'supported':bool(f and f.to_tuple()[0])})
failures=[r for r in rows if r['blocked'] or not r['supported']]
perimeter=runpy.run_path(str(OUT/'scripts/check_routes.py'))['RESULT'];original=hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'reopened':bool(JOB.get('reopen')),'retained_actors':len(before),'assemblies':6,'tables':6,'benches':12,'max_bounds_error_cm':max(errors),'top_heights_m':heights,'shader_errors':shaders,'interior_samples':len(rows),'interior_failures':failures,'perimeter':perimeter,'original_map_unchanged':original}
(dest/'verification.json').write_text(json.dumps(RESULT,indent=2));assert not failures,failures;assert not perimeter['failures'];assert original
