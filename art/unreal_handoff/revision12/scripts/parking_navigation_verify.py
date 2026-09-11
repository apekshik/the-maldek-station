import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
if JOB.get('reopen'):assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=aa.get_all_level_actors();by={a.get_actor_label():a for a in actors};before=json.loads((out/'before.json').read_text());o=before['origin']
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
def ground(p,keep):
 h=unreal.SystemLibrary.line_trace_single(w,wp([p[0],p[1],20]),wp([p[0],p[1],-30]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a for a in actors if a not in keep],unreal.DrawDebugTrace.NONE,True)
 return (h.to_tuple()[5].z-o[2])/100 if h and h.to_tuple()[0] else None
path=by['VF10_Parking_Forest_Connector'];terrain=[a for a in actors if isinstance(a,unreal.LandscapeProxy) or a.get_actor_label()=='VF10_Parking_Terrain']
samples=[]
for index,p in enumerate(json.loads((out/'plan.json').read_text())['centreline']):
 t=index/16;s=t*t*(3-2*t);half=1.6-.35*s
 for dx in [-half*.98,0,half*.98]:
  q=[p[0]+dx,p[1],p[2]];pz=ground(q,[path]);tz=ground(q,terrain);samples.append({'p':q,'path_z':pz,'terrain_z':tz,'clearance':pz-tz if pz is not None and tz is not None else None})
preserved=[]
for label in ['PlayerStart','FR_Parked_Hatchback','FR_Parked_Pickup','VF10_Parking_Ground']:
 r=next(r for r in before['actors'] if r['label']==label);a=by[label];assert (a.get_actor_location()-unreal.Vector(*r['world'])).length()<.01;preserved.append(label)
minimum=min(s['clearance'] for s in samples if s['clearance'] is not None)
assert all(s['path_z'] is not None for s in samples) and minimum>.02,('Path terrain clearance',minimum)
for r in json.loads((out/'installation.json').read_text())['assets']:
 assert by[r['label']].static_mesh_component.static_mesh.get_path_name()==r['mesh']
assert 'Parking_Navigation_Sign_Light' in by
intensity=by['Parking_Navigation_Sign_Light'].get_component_by_class(unreal.SpotLightComponent).get_editor_property('intensity');assert abs(intensity)<.001
RESULT={'passed':True,'reopened':bool(JOB.get('reopen')),'samples':samples,'preserved':preserved,'path_mesh':path.static_mesh_component.static_mesh.get_path_name(),'minimum_terrain_clearance_m':minimum,'sign_light_lumens':intensity}
(out/('reopen.json' if JOB.get('reopen') else 'floor_survey.json')).write_text(json.dumps(RESULT,indent=2))
