import unreal,json,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REV=OUT/'revision05';ROOT='/Game/MaldekRefinement/R05';MAP=ROOT+'/BlockOut_R05'
unreal.EditorPythonScripting.set_keep_python_script_alive(True)

lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='BlockOut_R05'
mp=ROOT+'/Materials/M_R03_Wet_Gravel'
m=lib.load_asset(mp)
if not m:
 m=at.create_asset('M_R03_Wet_Gravel',ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.075,.065,.05,1));ml.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=ml.create_material_expression(m,unreal.MaterialExpressionConstant);r.set_editor_property('r',.72);ml.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.recompile_material(m);lib.save_loaded_asset(m)
manifest=json.loads((REV/'export_manifest.json').read_text())
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
for row in manifest['chunks']:
 name=row['name'];task=unreal.AssetImportTask();task.filename=str(REV/'fbx'/(name+'.fbx'));task.destination_path=ROOT+'/Meshes';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 data=opt.static_mesh_import_data;data.combine_meshes=True;data.auto_generate_collision=False;data.convert_scene=True;data.convert_scene_unit=True;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
 task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(ROOT+'/Meshes/'+name)
 for i,s in enumerate(mesh.static_materials):
  m=lib.load_asset((ROOT+'/Materials/M_' if str(s.material_slot_name)=='R03_Wet_Gravel' else '/Game/MaldekRefinement/Materials/M_')+str(s.material_slot_name));assert m,str(s.material_slot_name);mesh.set_material(i,m)
 if row['collection']=='09_Relay_and_Paths':mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 lib.save_loaded_asset(mesh)
 label=name.replace('SM_R04_','R04_');a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 origin=json.loads((OUT/'working_level_report.json').read_text())['station_origin']
 if not a:a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*origin),unreal.Rotator(pitch=0,yaw=180,roll=0))
 a.set_actor_label(label);a.set_folder_path('R05_Completed_Route');a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll')
land=next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='Landscape')
mi=lib.duplicate_asset(land.get_editor_property('landscape_material').get_path_name(),ROOT+'/Materials/MI_Landscape_CohesiveSnow')
assert mi
ml.set_material_instance_vector_parameter_value(mi,'MW_SnowColorCorrection',unreal.LinearColor(.30,.35,.43,1))
lib.save_loaded_asset(mi);land.set_editor_property('landscape_material',mi)
assert levels.save_current_level()
# Sample a larger area so the restored relay paths have a grounded shoulder.
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ignore=[a for a in actors.get_all_level_actors() if a!=land]
rows=[]
for y in range(-80,97,2):
 row=[]
 for x in range(-96,113,2):
  wx=origin[0]-x*100;wy=origin[1]+y*100
  h=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(wx,wy,80000),unreal.Vector(wx,wy,-80000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
  assert h;row.append((h.to_tuple()[5].z-origin[2])/100)
 rows.append(row)
(REV/'terrain_samples.json').write_text(json.dumps({'origin':origin,'xmin':-96,'xmax':112,'ymin':-80,'ymax':96,'step':2,'heights':rows}))
(REV/'build_stage.json').write_text(json.dumps({'map':MAP,'restored':[r['collection'] for r in manifest['chunks']],'landscape_snow_tint':[.30,.35,.43],'saved':True}))

