import unreal,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';lib=unreal.EditorAssetLibrary;aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R11'
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];layout=json.loads((out/'layout.json').read_text());grid=json.loads((out/'terrain_grid.json').read_text())
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def ground(x,y):
 i=round(x-grid['xmin']);j=round(y-grid['ymin']);return grid['vertices'][j*grid['nx']+i][2] if 0<=i<grid['nx'] and 0<=j<len(grid['vertices'])//grid['nx'] else None
def distance(x,y):
 best=1e9
 for a,b in zip(layout['service_route'],layout['service_route'][1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return best
def bridge_distance(x,y):
 best=1e9
 for a,b in zip(layout['bridge_points'],layout['bridge_points'][1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return best
trees=[[],[],[]];removed=0
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
  mesh=c.static_mesh
  if not mesh or not mesh.get_name().startswith('SM_R06_Pine_'):continue
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,True);x=(origin[0]-t.translation.x)/100;y=(t.translation.y-origin[1])/100;z=ground(x,y)
   if distance(x,y)<3.4 or (25<x<38 and -27<y<-9) or bridge_distance(x,y)<6 or (12<x<26 and 27<y<41):removed+=1;continue
   if z is not None:t.translation=wp((x,y,z-.04))
   trees[int(mesh.get_name()[-1])].append(t)
for i,ts in enumerate(trees):
 ft=lib.load_asset('/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_'+str(i));unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
metal=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal');lens=lib.load_asset('/Game/MaldekRefinement/R08/Materials/M_WallLamp_Diffuser')
def fixture(name,p,target,intensity,size=(.22,.14,.12)):
 label='R11_'+name
 a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label+'_Housing'),None) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(p));a.set_actor_label(label+'_Housing');a.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,metal);a.set_actor_scale3d(unreal.Vector(*size));a.static_mesh_component.set_collision_profile_name('NoCollision')
 q=(p[0],p[1],p[2]-.075);a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label+'_Lens'),None) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(q));a.set_actor_label(label+'_Lens');a.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,lens);a.set_actor_scale3d(unreal.Vector(size[0]*.75,size[1]*.7,.02));a.static_mesh_component.set_collision_profile_name('NoCollision')
 a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label+'_Light'),None) or aa.spawn_actor_from_class(unreal.SpotLight,wp(q),unreal.MathLibrary.find_look_at_rotation(wp(q),wp(target)));a.set_actor_label(label+'_Light');c=a.light_component;c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(intensity);c.set_attenuation_radius(550);c.set_inner_cone_angle(15);c.set_outer_cone_angle(45);c.set_temperature(3300);c.set_editor_property('use_temperature',True);c.set_editor_property('volumetric_scattering_intensity',.035);c.set_editor_property('cast_shadows',True)
fixture('Lookout_Rail_Lamp',(21.42,36,5.08),(19.2,34.5,4),.16)
fixture('Generator_Entrance',(26.85,-15,1.65),(25.3,-15,-1),.32)
fixture('Generator_Ceiling',(30,-14,2.28),(30,-14,-1),.3,(.7,.15,.1))
fixture('Workshop_Ceiling',(34.5,-15.5,2.28),(34.5,-15.5,-1),.13,(.55,.15,.1))
fixture('Fuel_Yard_Exit',(30,-19.15,1.6),(30,-21,-1),.18)
# Ensure the inherited R10 details are present and align the relocated hall light.
sky=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky');angle=math.radians(90-sky.get_actor_rotation().yaw);sky.set_editor_property('Manually Position Moon Target',True);sky.set_editor_property('Moon Target',unreal.Vector(50*math.cos(angle),50*math.sin(angle),50*math.tan(math.radians(20))))
report={'pines_removed_from_route':removed,'pines_retained':sum(map(len,trees)),'fixtures':5}
for a in aa.get_all_level_actors():
 if a.get_actor_label()=='R08_WallLight_Waiting_Hall_Entry':report['waiting_lamp_location']=str(a.get_actor_location())
 if a.get_actor_label()=='R10_Forest_Wind':
  sound=lib.load_asset('/Game/MaldekRefinement/R10/Audio/Forest_Wind_Loop');a.audio_component.set_sound(sound or a.audio_component.sound);report['wind_sound']=str(a.audio_component.sound)
world.get_world_settings().set_editor_property('kill_z',0.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(out/'style_report.json').write_text(json.dumps(report,indent=2))
