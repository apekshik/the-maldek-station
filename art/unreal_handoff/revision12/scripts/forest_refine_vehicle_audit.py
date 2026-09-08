"""Inspect the imported parked vehicle candidates and their original materials."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine'/'vehicles';out.mkdir(parents=True,exist_ok=True)
ml=unreal.MaterialEditingLibrary;rows=[]
for name in ['SM_Hatchback','SM_Pickup']:
 m=unreal.load_asset('/Game/VehicleVarietyPack/Meshes/'+name);assert m
 bounds=m.get_bounds();materials=[]
 for slot in m.static_materials:
  mat=slot.material_interface
  materials.append({'slot':str(slot.material_slot_name),'path':mat.get_path_name(),'class':mat.get_class().get_name(),'scalar_names':[str(n) for n in ml.get_scalar_parameter_names(mat)],'vector_names':[str(n) for n in ml.get_vector_parameter_names(mat)],'texture_names':[str(n) for n in ml.get_texture_parameter_names(mat)]})
 row={'path':m.get_path_name(),'origin':list(bounds.origin.to_tuple()),'extent':list(bounds.box_extent.to_tuple()),'materials':materials,'collision_hulls':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_convex_collision_count(m)}
 task=unreal.AssetExportTask();task.object=m;task.filename=str(out/(name+'.fbx'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.StaticMeshExporterFBX();task.options=unreal.FbxExportOption();row['exported']=unreal.Exporter.run_asset_export_task(task)
 rows.append(row)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=[]
for a in aa.get_all_level_actors():
 if 'Car' in a.get_actor_label() or 'Parking' in a.get_actor_label():
  actors.append({'label':a.get_actor_label(),'location':list(a.get_actor_location().to_tuple()),'rotation':str(a.get_actor_rotation()),'bounds':str(a.get_actor_bounds(False))})
RESULT={'assets':rows,'parking_actors':actors};(out/'audit.json').write_text(json.dumps(RESULT,indent=2))
