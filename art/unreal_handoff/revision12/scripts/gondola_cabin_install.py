"""Install completed cabin assets into the existing route without moving its spline/terminals."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_cabin';manifest=json.loads((out/'manifest.json').read_text())
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
root='/Game/MaldekRefinement/R12/GondolaCabin';actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];assert g.door_left
prior_parts=[a.get_actor_label() for a in g.cabin_parts if a]
sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
carrier=next(c for c in g.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh');carrier.set_world_location(start,False,False);carrier.set_world_rotation(g.cabin_dock_rotation,False,False);carrier.set_world_scale3d(unreal.Vector(1,1,1))
route=[sp.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD).to_tuple() for i in range(sp.get_number_of_spline_points())]
mats={};created=[]
def val(m,v,prop):
 vector=isinstance(v,list);n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if vector else unreal.MaterialExpressionConstant);n.set_editor_property('constant' if vector else 'r',unreal.LinearColor(*v[:3],1) if vector else v);assert ml.connect_material_property(n,'',prop)
for info in manifest['materials'].values():
 slot=info['slot'];m=lib.load_asset(root+'/Materials/M_'+slot) or at.create_asset('M_'+slot,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 val(m,info['base_color'],unreal.MaterialProperty.MP_BASE_COLOR);val(m,info['roughness'],unreal.MaterialProperty.MP_ROUGHNESS);val(m,info['metallic'],unreal.MaterialProperty.MP_METALLIC)
 if info['glass']:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True);m.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING);val(m,.16,unreal.MaterialProperty.MP_OPACITY)
 if info['emission_strength']>0:val(m,[x*min(.6,info['emission_strength']) for x in info['emission_color'][:3]],unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 ml.recompile_material(m);lib.save_loaded_asset(m);mats[slot]=m;created.append(m)
assert not unreal.StationMigrationLibrary.validate_material_shaders(created)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');meshes={};rows=[]
for row in manifest['chunks']:
 file=out/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
 t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt;at.import_asset_tasks([t])
 mesh=lib.load_asset(root+'/Meshes/'+row['name']);assert mesh
 box=mesh.get_bounding_box();actual=[box.min.to_tuple(),box.max.to_tuple()];lo,hi=row['bounds'];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]];error=max(abs(actual[j][i]-wanted[j][i]) for j in range(2) for i in range(3));assert error<.1,(row['name'],error)
 for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(slot.material_slot_name)])
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True)
 if row['collision_hulls']==0:sm.remove_collisions(mesh)
 else:assert sm.get_convex_collision_count(mesh)==row['collision_hulls']
 lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;rows.append({'name':row['name'],'bounds_error_cm':error,'collision_hulls':sm.get_convex_collision_count(mesh)})
sounds={}
for name in ['Gondola_Door_Open','Gondola_Door_Close']:
 t=unreal.AssetImportTask();t.filename=str(b.parents[2]/'art/audio/gondola_doors/wav'/(name+'.wav'));t.destination_path=root+'/Audio';t.automated=True;t.save=True;t.replace_existing=True;at.import_asset_tasks([t]);sounds[name]=lib.load_asset(root+'/Audio/'+name);assert sounds[name]
 sounds[name].set_editor_property('looping',False);lib.save_loaded_asset(sounds[name])
# Imported assembly replaces every old shell/detail chunk, preventing doubled surfaces.
removed=[]
for label,a in list(actors.items()):
 if label.startswith(('R12_12_Gondola_','R12_VF06_Gondola_Details_')):
  removed.append(label);aa.destroy_actor(a);del actors[label]
for name in ['CabinShell','CabinGlass']:
 label='R12_Gondola_'+name;a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,start);a.set_actor_label(label);a.set_folder_path('R12/Gondola Cabin');a.set_actor_location(start,False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),True);a.set_actor_scale3d(unreal.Vector(1,1,1));c=a.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(meshes['SM_Gondola_'+name]);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if name=='CabinShell' else 'NoCollision');actors[label]=a
for c,name in [(g.door_left,'DoorLeft'),(g.door_right,'DoorRight'),(g.door_pinion,'Pinion')]:c.set_static_mesh(meshes['SM_Gondola_'+name]);c.set_editor_property('override_materials',[])
for c in g.door_rollers:c.set_static_mesh(meshes['SM_Gondola_Roller'])
for c in [g.door_left,g.door_right]:c.set_relative_location(unreal.Vector(),False,False);c.set_relative_rotation(unreal.Rotator(yaw=180),False,False)
g.door_pinion.set_relative_rotation(unreal.Rotator(yaw=180),False,False)
g.set_editor_property('door_open_sound',sounds['Gondola_Door_Open']);g.set_editor_property('door_close_sound',sounds['Gondola_Door_Close'])
part_labels=set(prior_parts)|{'R12_Gondola_CabinShell','R12_Gondola_CabinGlass'}
parts=[a for label,a in actors.items() if label in part_labels];g.set_editor_property('cabin_parts',parts)
for a in parts:
 for c in a.get_components_by_class(unreal.SceneComponent):c.set_mobility(unreal.ComponentMobility.MOVABLE)
for label,a in actors.items():
 if label.startswith('R12_Gondola_Interior_Light_'):assert a.point_light_component.get_editor_property('intensity')==12
assert route==[sp.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD).to_tuple() for i in range(sp.get_number_of_spline_points())]
assert ls.save_current_level()
RESULT={'success':True,'meshes':rows,'removed_old_chunks':removed,'cabin_parts':[a.get_actor_label() for a in parts],'route_preserved':True,'door_travel_cm':63.5,'recorded_sounds':[x.get_path_name() for x in sounds.values()]};(out/'install.json').write_text(json.dumps(RESULT,indent=2))
