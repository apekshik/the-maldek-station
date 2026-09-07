import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1];(out/'revision06').mkdir(exist_ok=True)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
runpy.run_path(str(Path(__file__).with_name('review_session.py')))
lib=unreal.EditorAssetLibrary;levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);root='/Game/MaldekRefinement/R06'
assert not lib.does_asset_exist(root+'/BlockOut_R06')
assert levels.new_level_from_template(root+'/BlockOut_R06','/Game/MaldekRefinement/R05/BlockOut_R05')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
land=next(a for a in actors if a.get_class().get_name()=='Landscape')
report={'landscape_api':[n for n in dir(land) if any(t in n for t in ['height','weight','import','export'])], 'conversion_api':[n for n in dir(unreal) if any(t in n for t in ['MeshConversion','SkeletalMeshLibrary','MeshMerge','GeometryScript','LandscapeEditor'])]}
for n in ['EditorSkeletalMeshLibrary','StaticMeshEditorSubsystem','SkeletalMeshEditorSubsystem']:
 c=getattr(unreal,n,None)
 if c:report[n]=[s for s in dir(c) if any(t in s for t in ['convert','static','mesh'])]
report['sky']={a.get_actor_label():[c.get_class().get_name()+':'+c.get_name() for c in a.get_components_by_class(unreal.ActorComponent)] for a in actors if 'Ultra_Dynamic' in a.get_actor_label()}
(out/'revision06/runtime_audit.json').write_text(json.dumps(report,indent=2))
