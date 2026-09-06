import unreal, json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];OUT.mkdir(exist_ok=True)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def vec(v):return [v.x,v.y,v.z]
def trans(t):return {'location':vec(t.translation),'rotation':str(t.rotation.rotator()),'scale':vec(t.scale3d)}
for path in ['/Game/BlockOut','/Game/Gaea_test','/Game/Untitled']:
 if not levels.load_level(path):continue
 data=[]
 for a in actors.get_all_level_actors():
  row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'folder':str(a.get_folder_path()),'transform':trans(a.get_actor_transform())}
  try:
   center,extent=a.get_actor_bounds(False);row['bounds']={'center':vec(center),'extent':vec(extent)}
  except Exception:pass
  row['meshes']=[]
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   mesh=c.get_editor_property('static_mesh')
   row['meshes'].append({'component':c.get_name(),'mesh':mesh.get_path_name() if mesh else None,'transform':trans(c.get_world_transform()),'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
  row['splines']=[]
  for c in a.get_components_by_class(unreal.SplineComponent):
   row['splines'].append({'name':c.get_name(),'points':[{'location':vec(c.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD)),'rotation':str(c.get_rotation_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD))} for i in range(c.get_number_of_spline_points())]})
  if 'Landscape' in row['class']:
   for prop in ['landscape_material','component_size_quads','subsection_size_quads','num_subsections']:
    try:row[prop]=str(a.get_editor_property(prop))
    except Exception:pass
  data.append(row)
 (OUT/(path.split('/')[-1]+'_inventory.json')).write_text(json.dumps(data,indent=2))
 unreal.log('HANDOFF_INSPECTED '+path+' '+str(len(data)))
