import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def v(p):return [p.x,p.y,p.z]
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
rows=[]
for a in aa.get_all_level_actors():
 p=local(a.get_actor_location());label=a.get_actor_label()
 if (-51<p[0]<-23 and -70<p[1]<-40) or any(k in label for k in ['Parking','Forest_Connector','PlayerStart','Car']):
  rows.append({'label':label,'position':p,'world':v(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'bounds':[v(x) for x in a.get_actor_bounds(False)],'meshes':[{'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]} for c in a.get_components_by_class(unreal.StaticMeshComponent)]})
RESULT={'world':w.get_path_name(),'origin':o,'actors':rows}
(out/'before.json').write_text(json.dumps(RESULT,indent=2))
