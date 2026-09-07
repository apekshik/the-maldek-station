import unreal,json,math,random
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';root='/Game/MaldekRefinement/R10';lib=unreal.EditorAssetLibrary;aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R10'
actors=aa.get_all_level_actors();sky=next(a for a in actors if a.get_actor_label()=='Ultra_Dynamic_Sky');weather=next(a for a in actors if a.get_actor_label()=='Ultra_Dynamic_Weather')
sky.set_editor_property('Manually Position Moon Target',True)
sky.set_editor_property('Moon Target',unreal.Vector(-44282,100000,43000))
sky.set_editor_property('Moon Yaw',90.);sky.set_editor_property('Moon Pitch',20.)
weather.set_editor_property('Enable Weather Sound Effects',True)
weather.set_editor_property('Weather Sounds Master Volume',.24)
weather.set_editor_property('Wind Volume',.65);weather.set_editor_property('Wind Whistling Volume',.22)
weather.set_editor_property('Rain Volume',.12);weather.set_editor_property('Distant Thunder Volume',.08);weather.set_editor_property('Close Thunder Volume',0.)
# Explicit soft tree-wind bed complements weather's positional whistling.
sound=lib.load_asset('/Game/UltraDynamicSky/Sound/Environment/Forest_Example/Waves/TreeWind/TreeWind_Light')
wind=next((a for a in actors if a.get_actor_label()=='R10_Forest_Wind'),None) or aa.spawn_actor_from_class(unreal.AmbientSound,unreal.Vector(-44282,18475,10300))
wind.set_actor_label('R10_Forest_Wind');wind.audio_component.set_sound(sound);wind.audio_component.set_volume_multiplier(.07);wind.audio_component.set_editor_property('auto_activate',True)
# Re-root retained pines to the edited terrain; drop those now inside the canyon.
grid=json.loads((out/'terrain_grid.json').read_text());vs=grid['vertices'];nx=grid['nx'];path=json.loads((out/'approach_path.json').read_text())['points'];origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
def ground(x,y):
 i=int(round(x-grid['xmin']));j=int(round(y-grid['ymin']))
 return vs[j*nx+i][2] if 0<=i<nx and 0<=j<len(vs)//nx else None
baseline=out/'foliage_before.json'
if baseline.exists():rows=json.loads(baseline.read_text())
else:
 rows=[]
 for a in actors:
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   mesh=c.static_mesh
   if not mesh or not mesh.get_name().startswith('SM_R06_Pine_'):continue
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,True);rows.append({'v':int(mesh.get_name()[-1]),'p':[t.translation.x,t.translation.y,t.translation.z],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z],'r':t.rotation.rotator().yaw})
 baseline.write_text(json.dumps(rows))
ts=[[],[],[]];positions=[]
def tree(x,y,s,yaw,v):
 z=ground(x,y)
 if z is None or z<-20:return
 if min((x-p[0])**2+(y-p[1])**2 for p in path)<3.8**2:return
 if -42<x<-30 and -65<y<-55:return
 if any((x-a)**2+(y-b)**2<3.8**2 for a,b in positions):return
 ts[v].append(unreal.Transform(location=unreal.Vector(origin[0]-100*x,origin[1]+100*y,origin[2]+100*z-4),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(*s)));positions.append((x,y))
for r in rows:
 x=(origin[0]-r['p'][0])/100;y=(r['p'][1]-origin[1])/100;tree(x,y,r['s'],r['r'],r['v'])
rng=random.Random(1010)
for i in range(320):
 x=rng.uniform(-55,65);y=rng.uniform(-73,26)
 # Concentrate foliage along arrival and on the flanking land, avoiding occupied buildings.
 if -20<x<23 and -19<y<14:continue
 if 42<x<56 and 7<y<20:continue
 if 9<x<29 and 0<y<19:continue
 s=rng.uniform(.85,1.25);tree(x,y,[s,s,s*rng.uniform(1.5,2.1)],rng.uniform(0,360),i%3)
for i,t in enumerate(ts):
 ft=lib.load_asset('/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_'+str(i));unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,t)
# A far station landmark, 650m along the cabin's outward +Y view.
m=lib.load_asset(root+'/Materials/M_Distant_Station_Lamp') or at.create_asset('M_Distant_Station_Lamp',root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(12,5,1.5,1);ml.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ml.recompile_material(m);lib.save_loaded_asset(m)
def box(label,p,s,material):
 a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label),None) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p));a.set_actor_label(label);a.set_actor_location(unreal.Vector(*p),False,False);a.set_actor_scale3d(unreal.Vector(*s));a.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,material);return a
# Ground the silhouette on the distant ridge by tracing only the Landscape.
land=next(a for a in actors if isinstance(a,unreal.Landscape));ignore=[a for a in aa.get_all_level_actors() if a!=land]
p=unreal.Vector(-44282,158475,100000);h=unreal.SystemLibrary.line_trace_single(world,p,unreal.Vector(p.x,p.y,-30000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE);z=h.to_tuple()[5].z if h and h.to_tuple()[0] else 32228
shell=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal')
box('R10_Distant_Station',[-44282,158475,z+200],[14,8,4],shell)
for i,x in enumerate([-44632,-44282,-43932]):box('R10_Distant_Window_'+str(i),[x,158069,z+240],[2.2,.04,1.1],m)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'environment_report.json').write_text(json.dumps({'pines':len(positions),'wind_master':.24,'wind_bed':.07,'remote_station_distance_m':650,'remote_ground_z':z,'moon_target':[-44282,100000,43000]},indent=2))
