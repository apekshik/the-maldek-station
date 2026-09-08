"""Apply the measured FBX basis (-X,+Y,+Z after 180-degree yaw) to route-only imports."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();root='/Game/MaldekRefinement/R12/GondolaRoute'
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
for i in ([] if globals().get('JOB',{}).get('skip_import') else range(1,6)):
 name='SM_Gondola_Pylon_%02d'%i;t=unreal.AssetImportTask();t.filename=str(out/'fbx'/(name+'.fbx'));t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;t.options=opt;at.import_asset_tasks([t])
 mesh=lib.load_asset(root+'/Meshes/'+name)
 for j,slot in enumerate(mesh.get_editor_property('static_materials')):
  mat=lib.load_asset(root+'/Materials/M_'+str(slot.get_editor_property('imported_material_slot_name')));assert mat;mesh.set_material(j,mat)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);lib.save_loaded_asset(mesh)
changed=[]
for label,a in actors.items():
 if label.startswith(('R12_Route_Pylon_','R12_Route_Cable_','R12_Route_Terminal_')) or label=='R12_Gondola_Hanger_Adapter':a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),True);changed.append(label)
cable=actors['R12_Route_Cable_Passenger'];centre,extent=cable.get_actor_bounds(False);plan=json.loads((out/'plan.json').read_text());assert abs(centre.y-extent.y-plan['nodes'][0]['y']*100)<2;assert abs(centre.y+extent.y-plan['nodes'][-1]['y']*100)<2
assert ls.save_current_level();RESULT={'saved':True,'rotated':changed,'cable_y_bounds_cm':[centre.y-extent.y,centre.y+extent.y]};(out/'orientation.json').write_text(json.dumps(RESULT,indent=2))
