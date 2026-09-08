import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
RESULT={'world':w.get_path_name(),'pie':ls.is_in_play_in_editor(),'native_door':hasattr(unreal,'StationDoor'),'actors':[]}
for a in aa.get_all_level_actors():
 if any(k in a.get_actor_label().lower() for k in ['control','door']):
  RESULT['actors'].append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':list(a.get_actor_location().to_tuple())})
RESULT['scene_color_properties']=unreal.MaterialExpressionSceneColor.__doc__
(out/'editor_audit.json').write_text(json.dumps(RESULT,indent=2))
