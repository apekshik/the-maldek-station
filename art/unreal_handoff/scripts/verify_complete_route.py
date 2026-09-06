import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R05'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();origin=json.loads((OUT/'working_level_report.json').read_text())['station_origin']
paths=json.loads((OUT.parents[1]/'art/blender/revision_03/route_points.json').read_text())['paths']
samples=[('overlook',[12,5,4]),('relay',[48,13,3])]+[(f'path_{i}_{j}',p) for i,path in enumerate(paths) for j,p in enumerate(path) if j%5==0]
rows=[]
for label,(x,y,z) in samples:
 p=unreal.Vector(origin[0]-x*100,origin[1]+y*100,origin[2]+z*100)
 hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(p.x,p.y,p.z+60),unreal.Vector(p.x,p.y,p.z-500),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE)
 h=hit.to_tuple() if hit else None
 row={'sample':label,'source':[x,y,z],'floor':h[9].get_actor_label() if h and h[0] and h[9] else None,'height_error_cm':h[5].z-p.z if h and h[0] else None}
 if h and h[0]:
  cap=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(p.x,p.y,h[5].z+92),unreal.Vector(p.x+1,p.y,h[5].z+92),34,88,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE)
  c=cap.to_tuple() if cap else None;row['capsule_blocked']=bool(c and c[0]);row['capsule_actor']=c[9].get_actor_label() if c and c[9] else None
 rows.append(row)
(OUT/'revision05/route_validation.json').write_text(json.dumps(rows,indent=2))
