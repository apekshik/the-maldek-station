import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh and any(s in (c.static_mesh.get_path_name()+a.get_actor_label()).lower() for s in ['terrain','landscape','canyon']):
   rows.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'visible':c.get_editor_property('visible'),'hidden_in_game':c.get_editor_property('hidden_in_game'),'actor_hidden':a.get_editor_property('hidden'),'bounds':str(unreal.SystemLibrary.get_component_bounds(c))})
RESULT=rows;(out/'surface_audit.json').write_text(json.dumps(rows,indent=2))
