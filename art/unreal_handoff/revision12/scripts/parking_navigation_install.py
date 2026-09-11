import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';m=json.loads((out/'handoff.json').read_text())
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);lib=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};before=json.loads((out/'before.json').read_text());o=before['origin']
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
bindings={r['slot']:r['instance'] for r in json.loads((b/'material_bindings.json').read_text())['materials']}
bindings['UE_Parking_Navigation_Gravel__Exterior']=next(r for r in before['actors'] if r['label']=='VF10_Parking_Forest_Connector')['meshes'][0]['materials'][0]
targets={'SM_Parking_Navigation_Furniture':'VF10_Parking_Furniture','SM_Parking_Navigation_Path':'VF10_Parking_Forest_Connector'}
for r in m['chunks']:
 assert hashlib.sha256((out/r['file']).read_bytes()).hexdigest()==r['sha256']
 for slot in r['material_slots']:assert slot in bindings and lib.does_asset_exist(bindings[slot]),slot
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
rows=[]
for r in m['chunks']:
 task=unreal.AssetImportTask();task.filename=str(out/r['file']);task.destination_path='/Game/MaldekRefinement/R12/ParkingNavigation';task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=lib.load_asset(task.destination_path+'/'+r['name']);assert mesh
 bd=mesh.get_bounds();lo,hi=r['bounds'];actual=[bd.origin-bd.box_extent,bd.origin+bd.box_extent];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
 err=max(abs([actual[j].x,actual[j].y,actual[j].z][i]-wanted[j][i]) for j in range(2) for i in range(3));assert err<.2,(r['name'],err)
 for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,lib.load_asset(bindings[str(slot.material_slot_name)]))
 count=sm.get_convex_collision_count(mesh);assert count==r['collision_hulls'],(count,r['collision_hulls'])
 lib.save_loaded_asset(mesh);a=actors[targets[r['name']]];c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll');c.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+r['physical_surface']))
 rows.append({'label':a.get_actor_label(),'mesh':mesh.get_path_name(),'bounds_error_cm':err,'collision_hulls':count})
# Reposition the encroaching willow and first marker together using baseline offsets.
moves=[]
for label,target in [('FT_Goat_Willow_030',[-37.3,-49.8]),('FT_Marker_1_Post',[-34.05,-49.7]),('FT_Marker_1_Cap',[-34.05,-49.7]),('FT_Marker_1_Lens',[-34.05,-49.7]),('FT_Marker_1_Light',[-34.05,-49.7])]:
 row=next(r for r in before['actors'] if r['label']==label);p=row['position'];q=[target[0],target[1],p[2]];actors[label].set_actor_location(wp(q),False,True);moves.append({'label':label,'before':p,'after':q})
# Sign is deliberately unlit; the player flashlight reveals it.
lamp=actors.get('Parking_Navigation_Sign_Light') or aa.spawn_actor_from_class(unreal.SpotLight,wp([-35.3,-52.65,1.29]))
lamp.set_actor_label('Parking_Navigation_Sign_Light');lamp.set_folder_path('R12/Parking');lamp.set_actor_location(wp([-35.3,-52.65,1.29]),False,True);lamp.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(wp([-35.3,-52.65,1.29]),wp([-35.3,-52.32,.6])),False)
lc=lamp.get_component_by_class(unreal.SpotLightComponent);lc.set_mobility(unreal.ComponentMobility.MOVABLE);lc.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);lc.set_intensity(0);lc.set_visibility(False);lamp.set_actor_hidden_in_game(True);lc.set_editor_property('attenuation_radius',400);lc.set_inner_cone_angle(48);lc.set_outer_cone_angle(70);lc.set_light_color(unreal.LinearColor(1,.74,.43));lc.set_editor_property('source_radius',1.5);lc.set_editor_property('volumetric_scattering_intensity',.15)
assert ls.save_current_level();RESULT={'saved':True,'assets':rows,'moved':moves};(out/'installation.json').write_text(json.dumps(RESULT,indent=2))
