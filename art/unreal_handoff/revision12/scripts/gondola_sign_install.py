"""Install the Blender-authored grid sign on the right-hand station roof."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_sign';manifest=json.loads((out/'manifest.json').read_text())
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];sp=g.get_components_by_class(unreal.SplineComponent)[0]
start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
route=[sp.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD).to_tuple() for i in range(sp.get_number_of_spline_points())]
parts=[a.get_path_name() for a in g.cabin_parts if a]
root='/Game/MaldekRefinement/R12/GondolaSign';mats={}
def constant(m,v):
 n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if isinstance(v,list) else unreal.MaterialExpressionConstant)
 n.set_editor_property('constant' if isinstance(v,list) else 'r',unreal.LinearColor(*v[:3],1) if isinstance(v,list) else v);return n
for info in manifest['materials'].values():
 slot=info['slot'];m=lib.load_asset(root+'/Materials/M_'+slot) or at.create_asset('M_'+slot,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for value,prop in [(info['base_color'],unreal.MaterialProperty.MP_BASE_COLOR),(info['roughness'],unreal.MaterialProperty.MP_ROUGHNESS),(info['metallic'],unreal.MaterialProperty.MP_METALLIC)]:assert ml.connect_material_property(constant(m,value),'',prop)
 if 'Circuit_' in info['source_material']:
  scalar=ml.create_material_expression(m,unreal.MaterialExpressionScalarParameter);scalar.set_editor_property('parameter_name','GlowStrength');scalar.set_editor_property('default_value',7 if info['source_material'].endswith('_AWAY') else .015)
  color=constant(m,info['emission_color']);mul=ml.create_material_expression(m,unreal.MaterialExpressionMultiply)
  assert ml.connect_material_expressions(color,'',mul,'A') and ml.connect_material_expressions(scalar,'',mul,'B') and ml.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 ml.recompile_material(m);lib.save_loaded_asset(m);mats[slot]=m
assert not unreal.StationMigrationLibrary.validate_material_shaders(list(mats.values()))
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
 if not row['collision_hulls']:sm.remove_collisions(mesh)
 assert sm.get_convex_collision_count(mesh)==row['collision_hulls']
 lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;rows.append({'name':row['name'],'bounds_error_cm':error,'collision_hulls':sm.get_convex_collision_count(mesh)})
label='R12_Gondola_Status_Sign';a=actors.get(label) or aa.spawn_actor_from_class(unreal.GondolaStatusSign,start)
a.set_actor_label(label);a.set_folder_path('R12/Gondola Status');a.set_actor_location(start+unreal.Vector(-220,-250,364),False,True);a.set_actor_rotation(unreal.Rotator(yaw=-90),True)
a.set_editor_property('gondola',g);a.set_editor_property('far_terminal',False)
a.set_editor_property('unlit_strength',0);a.set_editor_property('lit_strength',18)
a.cabinet.set_static_mesh(meshes['SM_Status_Cabinet'])
for c,word in zip(a.circuits,['BOARD','ARRIVING','DEPART','AWAY']):c.set_static_mesh(meshes['SM_Status_'+word])
assert not a.get_attach_parent_actor() and a not in g.cabin_parts
assert parts==[a.get_path_name() for a in g.cabin_parts if a]
assert route==[sp.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD).to_tuple() for i in range(sp.get_number_of_spline_points())]
# Find the real support surface beneath all four pedestal corners, ignoring the sign itself.
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();hits=[]
for x,y in [(x+dx,y) for x in [-92,92] for dx in [-9.5,9.5] for y in [-6.5,20.5]]:
 p=unreal.MathLibrary.transform_location(a.get_actor_transform(),unreal.Vector(x,-y,0))
 hit=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,60),p-unreal.Vector(0,0,100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a],unreal.DrawDebugTrace.NONE,True)
 assert hit and hit.to_tuple()[0],('No platform support',p)
 hits.append(hit.to_tuple()[5].z)
assert max(hits)-min(hits)<3,('Uneven support',hits)
a.set_actor_location(unreal.Vector(a.get_actor_location().x,a.get_actor_location().y,sum(hits)/len(hits)),False,True)
assert ls.save_current_level()
RESULT={'success':True,'meshes':rows,'position':a.get_actor_location().to_tuple(),'support_heights':hits,'route_preserved':True,'cabin_parts_preserved':True,'actor':a.get_path_name(),'placement':'Right-hand roof; facing left toward the incoming platform route','prior_map_sha256':hashlib.sha256((out/'pre_sign_working_map.umap').read_bytes()).hexdigest()};(out/'install.json').write_text(json.dumps(RESULT,indent=2))
