"""Survey all diagnosed terrain owners, excluding buildings and furniture."""
import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];b=json.loads((OUT/'before.json').read_text());o=b['origin']
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
owners=['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground'];terrain=[a for a in actors if a.get_actor_label() in owners];assert len(terrain)==3
ignore=[a for a in actors if a not in terrain]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
rows=[]
for x in range(-34,-4):
 for y in range(-24,11):
  h=unreal.SystemLibrary.line_trace_single(w,wp(x,y,15),wp(x,y,-40),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  t=h.to_tuple() if h else None
  rows.append({'xy':[x,y],'z':(t[5].z-o[2])/100 if t and t[0] else None,'actor':t[9].get_actor_label() if t and t[0] and t[9] else None})
(OUT/'ground_survey.json').write_text(json.dumps({'owners':owners,'samples':rows},indent=2))
RESULT={'samples':len(rows),'hits':sum(r['z'] is not None for r in rows)}
