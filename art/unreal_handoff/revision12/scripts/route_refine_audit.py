import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'route_refine';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def v(x):return [x.x,x.y,x.z]
rows=[]
for a in aa.get_all_level_actors():
 label=a.get_actor_label();splines=a.get_components_by_class(unreal.SplineComponent)
 if splines or any(k in label.lower() for k in ['distant','gondola','cable','pylon','pillar']):
  row={'label':label,'class':a.get_class().get_name(),'position':v(a.get_actor_location()),'scale':v(a.get_actor_scale3d()),'bounds':[v(x) for x in a.get_actor_bounds(False)],'meshes':[],'splines':[]}
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   row['meshes'].append({'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[str(c.get_material(i)) for i in range(c.get_num_materials())]})
  for c in splines:
   length=c.get_spline_length();row['splines'].append({'name':c.get_name(),'length':length,'points':[v(c.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD)) for i in range(c.get_number_of_spline_points())],'samples':[v(c.get_location_at_distance_along_spline(length*i/20,unreal.SplineCoordinateSpace.WORLD)) for i in range(21)]})
  rows.append(row)
RESULT={'world':w.get_path_name(),'pie':unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(),'actors':rows,'camera':str(unreal.EditorLevelLibrary.get_level_viewport_camera_info())}
(out/'audit.json').write_text(json.dumps(RESULT,indent=2))
