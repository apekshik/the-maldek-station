"""Park two original library vehicles, seating tires on the existing clearing."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine'/'vehicles';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];actors={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ground=[a for a in actors.values() if isinstance(a,unreal.Landscape) or a.get_actor_label() in ['VF10_Parking_Terrain','VF10_Parking_Ground','VF10_Parking_Forest_Connector']];ignore=[a for a in actors.values() if a not in ground]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
rows=[]
for vehicle,x,y,angle in [('Hatchback',-42.2,-60.0,86),('Pickup',-38.5,-61.0,97)]:
 label='FR_Parked_'+vehicle;mesh=unreal.load_asset('/Game/VehicleVarietyPack/Meshes/SM_'+vehicle);assert mesh
 ext=mesh.get_bounds().box_extent
 assert 250<max(ext.x,ext.y)*2<750,'Unexpected vehicle import dimensions'
 yaw=angle if ext.x>ext.y else angle-90
 a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(x,y,0));a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/Vehicles');a.set_actor_location(wp(x,y,0),False,True);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);a.set_actor_scale3d(unreal.Vector(1,1,1));c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('BlockAll');c.set_editor_property('override_materials',[])
 for i,slot in enumerate(mesh.static_materials):
  if slot.material_interface.get_name()==f'M_{vehicle}_Body':c.set_material(i,unreal.load_asset(f'/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Weathered_{vehicle}'))
 hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,50),wp(x,y,-100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore+[a],unreal.DrawDebugTrace.NONE,True);assert hit
 floor=hit.to_tuple()[5].z;bounds=a.get_actor_bounds(False);bottom_offset=bounds[0].z-bounds[1].z-a.get_actor_location().z;p=a.get_actor_location();p.z=floor-bottom_offset+.5;a.set_actor_location(p,False,True)
 rows.append({'label':label,'mesh':mesh.get_path_name(),'local':[x,y,(p.z-o[2])/100],'yaw':yaw,'tire_clearance_cm':.5,'materials':[c.get_material(i).get_path_name() for i in range(c.get_num_materials())],'collision_hulls':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_convex_collision_count(mesh)})
retired=[]
for label,a in actors.items():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh and c.static_mesh.get_name()=='SM_R12_Retained_Parked_Car':
   retired.append({'label':label,'mesh':c.static_mesh.get_path_name()});c.set_static_mesh(None);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
assert ls.save_current_level();RESULT={'vehicles':rows,'retired':retired,'saved':True};(out/'placement.json').write_text(json.dumps(RESULT,indent=2))
