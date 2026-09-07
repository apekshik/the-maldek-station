import unreal,json,random,math
from pathlib import Path
out=Path(__file__).resolve().parents[1];rev=out/'revision06';root='/Game/MaldekRefinement/R06';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);allactors=actors.get_all_level_actors();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R06'
land=next(a for a in allactors if a.get_class().get_name()=='Landscape');terrain=next(a for a in allactors if a.get_actor_label()=='R04_Local_Terrain')
mi=lib.duplicate_asset(land.get_editor_property('landscape_material').get_path_name(),root+'/Materials/MI_Snowy_Landscape');assert mi
ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowWorldPosition',-1500);ml.set_material_instance_vector_parameter_value(mi,'MW_SnowColorCorrection',unreal.LinearColor(.22,.27,.32,1));lib.save_loaded_asset(mi);land.set_editor_property('landscape_material',mi)
m=lib.duplicate_asset('/Game/MaldekRefinement/R05/Materials/M_R05_Local_Terrain',root+'/Materials/M_Snowy_Terrain');assert m
weather=ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
for pin,value in [('Mask Snow / Dust Coverage',1.0),('Offset Snow / Dust Coverage',.8)]:
 c=ml.create_material_expression(m,unreal.MaterialExpressionConstant);c.r=value;assert ml.connect_material_expressions(c,'',weather,pin)
ml.recompile_material(m);lib.save_loaded_asset(m)
mesh=lib.load_asset(root+'/Meshes/SM_R06_Local_Terrain');assert mesh;mesh.set_material(0,m);lib.save_loaded_asset(mesh);terrain.static_mesh_component.set_static_mesh(mesh);terrain.static_mesh_component.set_collision_profile_name('BlockAll')
for a in allactors:
 if 'Ultra_Dynamic' in a.get_actor_label():a.set_editor_property('Fog',6.5)
origin=json.loads((out/'working_level_report.json').read_text())['station_origin'];paths=json.loads((out.parents[1]/'art/blender/revision_03/route_points.json').read_text())['paths'];points=[p for path in paths for p in path]
rng=random.Random(606);locations=[];transforms=[[],[],[]]
ignore=[a for a in allactors if a not in [terrain,land]]
for attempt in range(12000):
 if len(locations)>=160:break
 x=rng.uniform(-65,90);y=rng.uniform(-45,90)
 if -25<x<21 and -23<y<17:continue
 if -20<x<20 and y>0:continue
 if 42<x<55 and 7<y<20:continue
 if 9<x<29 and 1<y<19:continue
 if min((x-p[0])**2+(y-p[1])**2 for p in points)<4**2:continue
 if any((x-p[0])**2+(y-p[1])**2<5.8**2 for p in locations):continue
 wx=origin[0]-x*100;wy=origin[1]+y*100
 hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(wx,wy,25000),unreal.Vector(wx,wy,-10000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
 h=hit.to_tuple() if hit else None
 if not h or not h[0] or h[6].z<.72:continue
 scale=rng.uniform(.65,1.18);p=unreal.Vector(wx,wy,h[5].z-5);rotation=unreal.Rotator(pitch=0,yaw=rng.uniform(0,360),roll=0)
 transforms[len(locations)%3].append(unreal.Transform(location=p,rotation=rotation,scale=unreal.Vector(scale,scale,scale*rng.uniform(.92,1.08))));locations.append([x,y,(h[5].z-origin[2])/100])
for i,ts in enumerate(transforms):
 ft=at.create_asset('FT_R06_Pine_'+str(i),root+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',lib.load_asset(root+'/Meshes/SM_R06_Pine_'+str(i)));ft.set_editor_property('cull_distance',unreal.Int32Interval(min=12000,max=18000));lib.save_loaded_asset(ft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(rev/'environment_placement.json').write_text(json.dumps({'trees':len(locations),'variants':[len(t) for t in transforms],'locations':locations,'fog':6.5,'snow_altitude':-1500,'saved':True},indent=2))
