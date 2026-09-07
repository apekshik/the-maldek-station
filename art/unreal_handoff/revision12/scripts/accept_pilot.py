import unreal,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1];world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Station_R12'
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
shader=json.loads((base/'shader_validation.json').read_text());capture=json.loads((base/'pilot/capture.json').read_text());imports=json.loads((base/'probe_import.json').read_text())
assert shader['success'] and capture['success'] and capture['inspection_lights_removed'] and imports['scale_and_axis_validated']
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);row=next(r for r in imports['assets'] if r['name']=='SM_R12_Probe_Door');a=next(a for a in aa.get_all_level_actors() if a.get_path_name()==row['actor']);p=a.get_actor_location();checks=[]
for name,x,expected in [('center',0,False),('left_jamb',65,True),('right_jamb',-65,True)]:
 hit=unreal.SystemLibrary.capsule_trace_single(world,p+unreal.Vector(x,-100,100),p+unreal.Vector(x,100,100),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
 blocked=bool(hit and hit.to_tuple()[0]);assert blocked==expected,(name,str(hit));checks.append({'name':name,'blocking':blocked,'expected':expected})
assert not any(a.get_actor_label()=='R12_Transient_Pilot_Lamp' for a in aa.get_all_level_actors())
report={'accepted':True,'scope':'Pilot scale, materials and doorway; full station route/visual acceptance remains separate','geometry_checks':checks,'render_review':['Teal paint and concrete grain visible under dry inspection lighting','Open grating remains real geometry','Yellow reference cube is visible through the glass pane','Existing night/Snow preset retained; inspection light and dry overrides removed'],'probe_manifest_sha256':hashlib.sha256((base/'probe_manifest.json').read_bytes()).hexdigest(),'shader_errors':[]}
(base/'pilot/acceptance.json').write_text(json.dumps(report,indent=2));unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();RESULT=report
