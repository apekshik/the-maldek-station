import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[2]/'revision13';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
r={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'pie':ls.is_in_play_in_editor(),'actors':[]}
for a in aa.get_all_level_actors():
 r['actors'].append({'path':a.get_path_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z],'components':[{'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None} for c in a.get_components_by_class(unreal.StaticMeshComponent)]})
(b/'live_before.json').write_text(json.dumps(r,indent=2));RESULT={'world':r['world'],'pie':r['pie'],'actors':len(r['actors'])}
