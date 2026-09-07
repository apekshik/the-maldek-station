import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';out.mkdir(exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name()=='BlockOut_R09':
 assert levels.save_current_level()
 assert levels.new_level_from_template('/Game/MaldekRefinement/R10/BlockOut_R10','/Game/MaldekRefinement/R09/BlockOut_R09')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R10'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
report=[]
for a in aa:
 row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':str(a.get_actor_transform())}
 if isinstance(a,unreal.StaticMeshActor):row['mesh']=a.static_mesh_component.static_mesh.get_path_name()
 if 'Ultra_Dynamic' in a.get_actor_label():
  row['fields']={n:str(getattr(a,n)) for n in dir(a) if any(s in n.lower() for s in ['moon','sound','audio','wind']) and not callable(getattr(a,n))}
 report.append(row)
(out/'initial_audit.json').write_text(json.dumps(report,indent=2))
runpy.run_path(str(Path(__file__).with_name('review_session.py')))
