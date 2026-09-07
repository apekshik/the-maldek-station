import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
def p(x,y,z):return unreal.Vector(origin[0]-100*x,origin[1]+100*y,origin[2]+100*z)
def trace(a,b,ignore=[]):
 h=unreal.SystemLibrary.line_trace_single(world,a,b,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
 if not h:return None
 v=h.to_tuple();return {'hit':v[0],'point':[v[5].x,v[5].y,v[5].z],'actor':str(v[9])}
r={}
for n,x,y in [('west_entry',-2.9,7),('west_end',-2.9,10.7),('east_infill',2.7,7.6),('east_end',2.7,10.7)]:r[n]=trace(p(x,y,4.5),p(x,y,3.5))
for n,x,y0,y1 in [('west_clear',-2.9,6.5,8),('east_clear',2.7,7.5,9)]:r[n]=trace(p(x,y0,4.6),p(x,y1,4.6))
ignore=[a for a in aa if a.get_class().get_name()!='Landscape' and a.get_actor_label()!='R04_Local_Terrain']
r['canyon']=[trace(p(x,25,10),p(x,25,-200),ignore) for x in [-20,0,15]]
path=json.loads((out/'approach_path.json').read_text())['points'];r['approach']=[trace(p(x,y,z+.5),p(x,y,z-.5)) for x,y,z in path[::8]]
sky=next(a for a in aa if a.get_actor_label()=='Ultra_Dynamic_Sky');r['moon']={}
for n in ['Moon Target','Moon World Rotation','Cached Moon Vector','Manually Position Moon Target','Moon Yaw','Moon Pitch']:
 try:r['moon'][n]=str(sky.get_editor_property(n))
 except:pass
land=next(a for a in aa if isinstance(a,unreal.Landscape));r['ridge_candidates']=[]
for d in [600,750,900,1100,1400]:
 for x in [-60,0,60]:r['ridge_candidates'].append({'xy':[x,d],'hit':trace(p(x,d,1000),p(x,d,-300),[a for a in aa if a!=land])})
(out/'geometry_verification.json').write_text(json.dumps(r,indent=2))
