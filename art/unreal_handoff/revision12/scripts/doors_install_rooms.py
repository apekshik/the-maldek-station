import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'doors';root='/Game/MaldekRefinement/R12/Doors';lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');at=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
original=lib.load_asset(root+'/Meshes/SM_StationDoor_Leaf');mats={str(s.material_slot_name):s.material_interface for s in original.static_materials}
for part in ['Fixed','Glass']:
 mats.update({str(s.material_slot_name):s.material_interface for s in lib.load_asset(root+'/Meshes/SM_StationDoor_'+part).static_materials})
for row in json.loads((out/'room_leaf_manifest.json').read_text())['chunks']+json.loads((out/'inward_manifest.json').read_text())['chunks']:
 file=out/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt;at.import_asset_tasks([t]);mesh=lib.load_asset(root+'/Meshes/'+row['name']);assert mesh
 for i,s in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(s.material_slot_name)])
 sm.remove_collisions(mesh);ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh)
# Original purpose-made mono effects; no changes to the station's existing audio banks.
sounds={};mapping={'button_sound':'KeyPress','clear_sound':'KeyClear','confirm_sound':'KeyConfirm','reject_sound':'KeyReject','unlatch_sound':'DoorUnlatch','movement_sound':'DoorMovement','close_sound':'DoorClose'}
for prop,name in mapping.items():
 t=unreal.AssetImportTask();t.filename=str(repo/'art/audio/doors/wav'/(name+'.wav'));t.destination_path=root+'/Audio';t.automated=True;t.save=True;t.replace_existing=True;at.import_asset_tasks([t]);sound=lib.load_asset(root+'/Audio/'+name);assert sound;sound.set_editor_property('looping',name=='DoorMovement');lib.save_loaded_asset(sound);sounds[prop]=sound
for name in ['Standard','Keypad']:
 bp=lib.load_asset(root+'/BP_StationDoor_'+name);cdo=unreal.get_default_object(bp.generated_class())
 for prop,sound in sounds.items():cdo.set_editor_property(prop,sound)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);lib.save_loaded_asset(bp)
cls=lib.load_blueprint_class(root+'/BP_StationDoor_Standard');origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};preserved={n:a.get_actor_transform() for n,a in actors.items() if not n.startswith('R12_Door_')}
# name, plaque, axis, plane, lower/upper jamb, floor, clear height, facing yaw, indoor
specs=[('Quarters','Quarters','X',-4.5,-2.65,-1.6,7.65,2.3,180,False),('Hall_north','Hall','X',0,-11,-9.5,4,2.4,0,False),('Hall_south','Hall','X',-7.8,-13.9,-12.4,4,2.4,180,False),('Generator_south','Generator','X',-19,28.7,30.3,-1,2.65,180,False),('Generator_west','Generator','Y',27,-15.85,-14.15,-1,2.65,-90,False),('Workshop_shared','Workshop','Y',37,-16.3,-14.7,-1,2.65,90,True)]
obsolete=actors.get('R12_Door_Generator_north')
if obsolete:aa.destroy_actor(obsolete)
rows=[]
for name,plaque,axis,fixed,lo,hi,z,height,yaw,indoor in specs:
 sx=(hi-lo-.012)/1.288;bottom=.026 if name.startswith(('Generator','Workshop')) else .034;sz=(height-bottom-.006)/2.36;dz=bottom-.034*sz;u=hi-.006+.002*sx if yaw in [0,-90] else lo+.006-.002*sx
 inward=name in ['Quarters','Generator_south'];v=fixed+(.035 if yaw in [0,90] else -.035)*(-1 if inward else 1);pos=(u,v,z+dz) if axis=='X' else (v,u,z+dz)
 label='R12_Door_'+name;a=actors.get(label) or aa.spawn_actor_from_class(cls,wp(pos),unreal.Rotator(yaw=yaw));a.set_actor_label(label);a.set_folder_path('R12/Architecture/Doors');a.set_actor_location(wp(pos),False,True);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);a.set_actor_scale3d(unreal.Vector(sx,1,sz));a.set_editor_property('has_keypad',False);a.set_editor_property('locked',False);a.set_editor_property('access_code','');a.set_editor_property('open_angle',-95 if inward else 95);a.leaf.set_static_mesh(lib.load_asset(root+'/Meshes/SM_StationDoor_'+plaque+('InwardLeaf' if inward else 'Leaf')));a.glass.set_static_mesh(lib.load_asset(root+'/Meshes/SM_StationDoor_'+('InwardGlass' if inward else 'Glass')));a.fixed_hardware.set_static_mesh(lib.load_asset(root+'/Meshes/SM_StationDoor_'+('InwardFixed' if inward else 'Fixed')));a.leaf_collision.set_relative_location(unreal.Vector(64.6,3.5 if inward else -3.5,121.4),False,False)
 if indoor:
  for c in [a.leaf,a.fixed_hardware]:
   for i,slot in enumerate(c.static_mesh.static_materials):
    if str(slot.material_slot_name).startswith('UE_VF06_'):
     mat=lib.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_'+str(slot.material_slot_name)+'__Indoor')
     if mat:c.set_material(i,mat)
 rows.append({'label':label,'source_position':pos,'clear_width':hi-lo,'clear_height':height,'yaw':yaw,'inward':inward,'scale':[sx,1,sz]})
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.StationDoor):
  for prop,sound in sounds.items():a.set_editor_property(prop,sound)
for n,t in preserved.items():assert actors[n].get_actor_transform()==t,n
assert ls.save_current_level();RESULT={'success':True,'new_doors':rows,'total_doors':10,'other_actors_preserved':len(preserved),'sound_assets':{k:v.get_path_name() for k,v in sounds.items()}};(out/'rooms_install.json').write_text(json.dumps(RESULT,indent=2))
