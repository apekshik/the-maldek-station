import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.editor_request_end_play()
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component;rows.append({'label':a.get_actor_label(),'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
(out/'audio_surfaces.json').write_text(json.dumps(rows,indent=2))
