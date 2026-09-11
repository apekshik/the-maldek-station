import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=aa.get_all_level_actors();by={a.get_actor_label():a for a in actors};o=json.loads((out/'before.json').read_text())['origin']
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
ground=[a for a in actors if isinstance(a,unreal.LandscapeProxy) or a.get_actor_label()=='VF10_Parking_Terrain'];ignore=[a for a in actors if a not in ground]
def z(p):
 h=unreal.SystemLibrary.line_trace_single(w,wp([p[0],p[1],20]),wp([p[0],p[1],-30]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 assert h and h.to_tuple()[0];return (h.to_tuple()[5].z-o[2])/100
rows=[]
for r in json.loads((out/'installation.json').read_text())['moved']:
 p=r['before'];q=r['after'][:];dz=z(q)-z(p);q[2]+=dz;by[r['label']].set_actor_location(wp(q),False,True);rows.append({'label':r['label'],'terrain_delta_m':dz,'position':q})
lamp=by['Parking_Navigation_Sign_Light'];lamp.set_actor_location(wp([-35.3,-52.65,1.29]),False,True);lamp.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(wp([-35.3,-52.65,1.29]),wp([-35.3,-52.32,.6])),False);lamp.get_component_by_class(unreal.SpotLightComponent).set_editor_property('source_radius',1.5)
assert ls.save_current_level();RESULT={'saved':True,'grounded':rows};(out/'grounded_details.json').write_text(json.dumps(RESULT,indent=2))
