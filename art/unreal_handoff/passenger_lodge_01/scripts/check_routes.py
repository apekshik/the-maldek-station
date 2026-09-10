import unreal,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin']
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
paths={'Entry':[[-23.1,-14.3,4],[-17.1,-14.3,4],[-17.1,-6.8,4]],'Platform':[[-17.1,5.5,4],[-4,5.5,4]],'Bypass':[[-17.1,-14.3,4],[-9.1,-14.3,4],[-9.1,-6.6,4],[-3.5,-6.6,4]],'West':[[-28,-14,4],[-28,5.5,4]]}
ignored=[a for a in actors if a.get_actor_label() in ['R12_Door_Hall_north','R12_Door_Hall_south']]
rows=[]
for name,path in paths.items():
 for a,b in zip(path,path[1:]):
  n=max(1,math.ceil(math.dist(a,b)/.25))
  for i in range(n+1):
   p=[x+(y-x)*i/n for x,y in zip(a,b)];center=wp([p[0],p[1],p[2]+.99])
   h=unreal.SystemLibrary.capsule_trace_single(w,center,center+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,True)
   block=h.to_tuple() if h else None
   f=unreal.SystemLibrary.sphere_trace_single(w,wp([p[0],p[1],p[2]+.15]),wp([p[0],p[1],p[2]-.3]),10,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,True)
   rows.append({'route':name,'point':p,'blocked':bool(block and block[0]),'actor':block[9].get_actor_label() if block and block[0] and block[9] else None,'supported':bool(f and f.to_tuple()[0])})
RESULT={'radius_cm':34,'half_height_cm':96,'conditions':'Editor collision queries; old hall doors ignored pending replacement. No PIE traversal yet.','samples':len(rows),'failures':[r for r in rows if r['blocked'] or not r['supported']]}
(OUT/'route_checks.json').write_text(json.dumps(RESULT,indent=2))
