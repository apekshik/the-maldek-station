import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_actor_label()=='TEMP_R11_Inspection':aa.destroy_actor(a)
assert not any(a.get_actor_label()=='TEMP_R11_Inspection' for a in aa.get_all_level_actors())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level()
(out/'play_ready.json').write_text(json.dumps({'saved_without_inspection_lights':True,'level':'/Game/MaldekRefinement/R11/BlockOut_R11','start':'parking approach'}))
levels.editor_request_begin_play()
