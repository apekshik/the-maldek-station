"""Capture a rollback and current terrain before the nighttime gorge pass."""
import unreal,json,shutil
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor(),'End the current play session first'
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def loc(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
rows=[]
for a in aa.get_all_level_actors():
 c=a.get_components_by_class(unreal.StaticMeshComponent)
 rows.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'local':loc(a.get_actor_location()),'transform':str(a.get_actor_transform()),'meshes':[v.static_mesh.get_path_name() for v in c if v.static_mesh]})
assert ls.save_current_level()
backup=out/'Station_R12_before_gorge.umap'
assert not backup.exists(),'Do not overwrite rollback'
shutil.copy2(b.parents[2]/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
(out/'before.json').write_text(json.dumps({'origin':o,'actors':rows},indent=2))
p=Path(__file__).resolve().parent/'export_landscape.py'
exec(compile(p.read_text().replace('base=Path(__file__).resolve().parents[1];',"base=Path(__file__).resolve().parents[1]/'gorge';"),str(p),'exec'))
