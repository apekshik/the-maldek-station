import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary
rows=[]
for species in ['European_Beech','Goat_Willow','European_Aspen']:
 for v in 'ABCD':
  p=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{v}'
  m=lib.load_asset(p)
  if m:
   rows.append({'path':p,'class':m.get_class().get_name(),'bounds':str(m.get_bounds())})
actors=[]
for a in aa.get_all_level_actors():
 actors.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'mesh':str(a.static_mesh_component.static_mesh) if isinstance(a,unreal.StaticMeshActor) else ''})
(out/'audit.json').write_text(json.dumps({'world':str(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()),'assets':rows,'actors':actors},indent=2))
