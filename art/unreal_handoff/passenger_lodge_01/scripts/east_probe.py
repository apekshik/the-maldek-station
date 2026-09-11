import unreal,json
from pathlib import Path
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
RESULT=[{'name':x.get_name(),'label':x.get_actor_label()} for x in a.get_all_level_actors() if x.get_name()=='StaticMeshActor_889']
print(RESULT)
