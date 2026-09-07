import unreal,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:continue
  nanite=c.static_mesh.get_editor_property('nanite_settings').enabled
  for i in range(c.get_num_materials()):
   mat=c.get_material(i)
   if not mat:continue
   chain=[mat];seen=set()
   while isinstance(chain[-1],unreal.MaterialInstance):
    p=chain[-1].get_editor_property('parent')
    if not p or p.get_path_name() in seen:break
    seen.add(p.get_path_name());chain.append(p)
   if chain[-1].get_path_name().startswith('/Fab/'):
    rows.append({'actor':a.get_path_name(),'label':a.get_actor_label(),'component':c.get_name(),'slot':i,'nanite':nanite,'chain':[m.get_path_name() for m in chain]})
(base/'retained_material_audit.json').write_text(json.dumps(rows,indent=2));RESULT={'Fab_material_slots':len(rows),'Nanite_slots':sum(r['nanite'] for r in rows)}
