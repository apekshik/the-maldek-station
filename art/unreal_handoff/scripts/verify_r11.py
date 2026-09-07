import unreal,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];layout=json.loads((out/'layout.json').read_text())
def p(x,y,z):return unreal.Vector(origin[0]-100*x,origin[1]+100*y,origin[2]+100*z)
def hit(a,b,ignore=[]):
 h=unreal.SystemLibrary.line_trace_single(world,a,b,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
 if not h:return None
 t=h.to_tuple();return {'blocking':t[0],'z':t[5].z,'actor':str(t[9])}
report={'bridge':[],'service':[]}
for name,route in [('bridge',layout['bridge_points']),('service',layout['service_route'])]:
 for a,b in zip(route,route[1:]):
  for i in range(math.ceil(math.dist(a,b)*2)+1):
   t=i/math.ceil(math.dist(a,b)*2);x,y,z=[v+(w-v)*t for v,w in zip(a,b)];h=hit(p(x,y,z+.3),p(x,y,z-.35));report[name].append({'position':[x,y,z],'floor':h})
report['rooms']={n:hit(p(x,y,z+.3),p(x,y,z-.5)) for n,x,y,z in [('generator',28,-15,-1),('workshop',34,-15.5,-1),('tank_yard',34,-22,-1),('lookout',19,35,4)]}
report['doorways']={n:hit(p(*a),p(*b)) for n,a,b in [('generator',(26.5,-15,0),(27.5,-15,0)),('workshop',(32.5,-15.5,0),(33.5,-15.5,0)),('fuel',(30,-18.5,0),(30,-19.5,0))]}
report['bridge_ground']=[hit(p(x,y,3),p(x,y,-200),[a for a in aa if a.get_actor_label()!='R04_Local_Terrain' and not isinstance(a,unreal.Landscape)]) for x,y in [(16,15),(19,34)]]
report['route_floor_pass']=all(v['floor'] and v['floor']['blocking'] for name in ['bridge','service'] for v in report[name]);report['doors_pass']=all(v is None or not v['blocking'] for v in report['doorways'].values())
sky=next(a for a in aa if a.get_actor_label()=='Ultra_Dynamic_Sky');report['moon_rotation']=str(sky.get_editor_property('Moon World Rotation'))
(out/'geometry_verification.json').write_text(json.dumps(report,indent=2))
