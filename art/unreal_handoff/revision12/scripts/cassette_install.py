import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/blender/cassette_01'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
t=unreal.AssetImportTask();t.filename=str(out/'SM_ServiceCassette.fbx');t.destination_path='/Game/Inspection/Cassette';t.destination_name='SM_ServiceCassette';t.automated=True;t.replace_existing=True;t.save=True
o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=unreal.load_asset('/Game/Inspection/Cassette/SM_ServiceCassette');assert mesh
mats={};ml=unreal.MaterialEditingLibrary
for spec in json.loads((out/'export_report.json').read_text())['materials']:
 name='M_'+spec['name'];path='/Game/Inspection/Cassette/'+name;m=unreal.load_asset(path)
 if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Inspection/Cassette',unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*spec['color'],1);ml.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val in [(unreal.MaterialProperty.MP_METALLIC,spec['metallic']),(unreal.MaterialProperty.MP_ROUGHNESS,spec['roughness'])]:
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant);n.r=val;ml.connect_material_property(n,'',prop)
 if spec['window']:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True)
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant);n.r=.22;ml.connect_material_property(n,'',unreal.MaterialProperty.MP_OPACITY)
 ml.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);mats[spec['name']]=m
slots=[]
for i,slot in enumerate(mesh.static_materials):
 name=str(slot.material_slot_name);assert name in mats,name
 mesh.set_material(i,mats[name]);slots.append(name)
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);sm.remove_collisions(mesh);sm.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=list(aa.get_all_level_actors());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/MaldekRefinement/R12/Station_R12.')
before={a.get_path_name():a.get_actor_transform() for a in actors}
truck=next(a for a in actors if a.get_actor_label()=='FR_Parked_Pickup');p=unreal.MathLibrary.transform_location(truck.get_actor_transform(),unreal.Vector(175,-17,0))
hit=unreal.SystemLibrary.line_trace_single(world,p+unreal.Vector(0,0,350),p-unreal.Vector(0,0,350),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a for a in actors if a!=truck],unreal.DrawDebugTrace.NONE,True).to_tuple();assert hit[0]
normal=hit[6];rot=unreal.MathLibrary.make_rot_from_yz(normal,truck.get_actor_forward_vector())
obj=next((a for a in actors if a.actor_has_tag('ParkingInspectionCassette')),None)
if not obj:obj=aa.spawn_actor_from_class(unreal.StationInspectable,hit[5],rot)
obj.set_actor_label('Inspection_Cassette_Pickup_Hood');obj.set_folder_path('R12/Inspection');obj.tags=['ParkingInspectionCassette'];obj.mesh.set_static_mesh(mesh);obj.mesh.set_simulate_physics(False)
obj.set_actor_location_and_rotation(hit[5]+normal*.76+unreal.Vector(0,0,6),rot,False,True);obj.set_actor_scale3d(unreal.Vector(1,1,1))
obj.set_editor_property('display_name','Millford field cassette — A / B');obj.set_editor_property('description','Night shift, 14 November 1986. Turn over to read the return label.');obj.set_editor_property('inspection_rotation',unreal.Rotator(yaw=90))
for a in actors:
 if a!=obj:assert a.get_actor_transform()==before[a.get_path_name()],a.get_actor_label()
assert ls.save_current_level();aa.set_selected_level_actors([obj])
RESULT={'saved':True,'mesh':mesh.get_path_name(),'label':obj.get_actor_label(),'location':obj.get_actor_location().to_tuple(),'rotation':rot.to_tuple(),'slots':slots,'other_actor_transforms_preserved':True}
(out/'unreal_install.json').write_text(json.dumps(RESULT,indent=2))
