import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_route'
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if any(k in a.get_actor_label().lower() for k in ['gondola','drive','flywheel','bullwheel','motor']):
  r={'label':a.get_actor_label(),'position':str(a.get_actor_location()),'lights':[],'materials':[]}
  for c in a.get_components_by_class(unreal.LightComponent):r['lights'].append({'name':c.get_name(),'intensity':c.intensity})
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   for i in range(c.get_num_materials()):
    m=c.get_material(i)
    if m:
     d={'path':m.get_path_name()}
     if isinstance(m,unreal.MaterialInstanceConstant):
      d['scalars']=[str(x) for x in m.get_editor_property('scalar_parameter_values')];d['vectors']=[str(x) for x in m.get_editor_property('vector_parameter_values')]
     r['materials'].append(d)
  rows.append(r)
(out/'brightness_audit.json').write_text(json.dumps(rows,indent=2));RESULT={'actors':len(rows)}
