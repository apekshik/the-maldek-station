import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'trim2';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
root='/Game/MaldekRefinement/R12/GondolaMarkers';materials={}
for name,color,metal,rough,emission in [('Marker_Base',(.025,.029,.031),.8,.3,None),('Marker_Red_Lens',(.3,.002,.001),.05,.2,(3,.009,.003))]:
 path=root+'/M_'+name;m=lib.load_asset(path) if lib.does_asset_exist(path) else at.create_asset('M_'+name,root,unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for val,prop in [(color,unreal.MaterialProperty.MP_BASE_COLOR),(metal,unreal.MaterialProperty.MP_METALLIC),(rough,unreal.MaterialProperty.MP_ROUGHNESS),(emission,unreal.MaterialProperty.MP_EMISSIVE_COLOR)]:
  if val is None:continue
  vec=isinstance(val,tuple);n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if vec else unreal.MaterialExpressionConstant)
  n.set_editor_property('constant' if vec else 'r',unreal.LinearColor(*val,1) if vec else val);ml.connect_material_property(n,'',prop)
 ml.recompile_material(m);lib.save_loaded_asset(m);materials[name]=m
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
path=root+'/SM_Gondola_Roof_Markers';task=unreal.AssetImportTask();task.filename=str(out/'SM_Gondola_Roof_Markers.fbx');task.destination_path=root;task.automated=True;task.save=True;task.replace_existing=True
opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path);assert mesh
for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,materials[str(slot.material_slot_name)])
unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).remove_collisions(mesh);lib.save_loaded_asset(mesh)
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};parent=actors['R12_12_Gondola_008_solid'];before=(parent.get_actor_location().to_tuple(),parent.get_actor_rotation().to_tuple(),parent.get_actor_scale3d().to_tuple())
marker=actors.get('R12_Gondola_Roof_Markers') or aa.spawn_actor_from_class(unreal.StaticMeshActor,parent.get_actor_location(),parent.get_actor_rotation());marker.set_actor_label('R12_Gondola_Roof_Markers');marker.set_actor_transform(parent.get_actor_transform(),False,True);marker.static_mesh_component.set_static_mesh(mesh);marker.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);marker.static_mesh_component.set_cast_shadow(False)
marker.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
layout=json.loads((out/'marker_layout.json').read_text());o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];lights=[]
for i,k in enumerate([2,7]):
 x,y,z=layout['roof_contact_points'][k];pos=unreal.Vector(o[0]-x*100,o[1]+y*100,o[2]+(z+.08)*100);label='R12_Gondola_Marker_Spill_'+str(i)
 a=actors.get(label) or aa.spawn_actor_from_class(unreal.PointLight,pos);a.set_actor_label(label);a.set_actor_location(pos,False,True);c=a.point_light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(.015);c.set_attenuation_radius(65);c.set_light_color(unreal.LinearColor(1,.006,.002,1));c.set_cast_shadows(False);c.set_indirect_lighting_intensity(0);c.set_volumetric_scattering_intensity(0)
 a.attach_to_actor(marker,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False);lights.append(label)
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished');cdo=unreal.get_default_object(bp.generated_class());presentation=cdo.get_component_by_class(unreal.StationPlayerPresentationComponent);presentation.set_editor_property('focused_lumens',1.35);presentation.set_editor_property('ground_height_response',18);lib.save_loaded_asset(bp,False)
assert (parent.get_actor_location().to_tuple(),parent.get_actor_rotation().to_tuple(),parent.get_actor_scale3d().to_tuple())==before;assert ls.save_current_level();errors=list(unreal.StationMigrationLibrary.validate_material_shaders(list(materials.values())));assert not errors
r={'success':True,'marker_count':10,'new_mesh_actors':1,'spill_lights':lights,'beam_focused_lumens':1.35,'beam_previous_focused_lumens':1.0,'wide_lumens':presentation.get_editor_property('wide_lumens'),'ground_height_response':18,'gondola_transform_preserved':True,'marker_collision':'NoCollision','material_errors':errors};(out/'setup.json').write_text(json.dumps(r,indent=2));RESULT=r
