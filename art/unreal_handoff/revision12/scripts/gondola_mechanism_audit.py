import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_mechanism';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def v(p):return [p.x,p.y,p.z]
rows=[]
for a in aa.get_all_level_actors():
 if any(k in a.get_actor_label() for k in ['Lower_Drive','Route_Terminal','Audio_Flywheel','Route_Cable','Upper_Platform']):
  row={'label':a.get_actor_label(),'position':v(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'bounds':[v(p) for p in a.get_actor_bounds(False)],'meshes':[]}
  for c in a.get_components_by_class(unreal.StaticMeshComponent):row['meshes'].append({'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() for i in range(c.get_num_materials())]})
  rows.append(row)
RESULT={'actors':rows};(out/'audit.json').write_text(json.dumps(RESULT,indent=2))
