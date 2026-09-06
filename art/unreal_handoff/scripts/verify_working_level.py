import unreal,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MaldekRefinement/Maps/BlockOut_R04')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def vec(v):return [v.x,v.y,v.z]
def transform(t):
 r=t.rotation.rotator();return {'location':vec(t.translation),'rotation':[r.pitch,r.yaw,r.roll],'scale':vec(t.scale3d)}
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
data=[]
for a in actors.get_all_level_actors():
 center,extent=a.get_actor_bounds(False)
 row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':transform(a.get_actor_transform()),'bounds':{'center':vec(center),'extent':vec(extent)},'meshes':[],'splines':[]}
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  mesh=c.get_editor_property('static_mesh')
  row['meshes'].append({'name':c.get_name(),'mesh':mesh.get_path_name() if mesh else None,'transform':transform(c.get_world_transform()),'visible':c.is_visible(),'collision':str(c.get_collision_enabled()),'parent':str(c.get_attach_parent())})
 for c in a.get_components_by_class(unreal.SplineComponent):
  row['splines'].append({'name':c.get_name(),'points':[vec(c.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD)) for i in range(c.get_number_of_spline_points())]})
 data.append(row)
(OUT/'working_inventory.json').write_text(json.dumps(data,indent=2))
(OUT/'trace_api.txt').write_text(str(unreal.SystemLibrary.line_trace_single.__doc__)+'\n'+str(unreal.HitResult.__doc__))
unreal.log('R04_VERIFY '+str(len(data)))
