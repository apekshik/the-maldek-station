"""Read newly imported rock assets; export a small shape review set."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine'/'rocks';out.mkdir(parents=True,exist_ok=True)
ml=unreal.MaterialEditingLibrary;rows=[]
paths=unreal.EditorAssetLibrary.list_assets('/Game/RockEnv_Pack/Meshes',True,False)
for p in paths:
 if not any('/'+s+'/' in p for s in ['Rocks','Small_Rocks','Jungle_Rocks']):continue
 m=unreal.load_asset(p)
 if not isinstance(m,unreal.StaticMesh):continue
 bounds=m.get_bounds(); mats=[]
 for slot in m.static_materials:
  mi=slot.material_interface
  mats.append({'path':mi.get_path_name(),'scalars':{str(n):ml.get_material_instance_scalar_parameter_value(mi,n) for n in ml.get_scalar_parameter_names(mi)} if isinstance(mi,unreal.MaterialInstanceConstant) else {},'vector_names':[str(n) for n in ml.get_vector_parameter_names(mi)]})
 row={'path':p,'origin':list(bounds.origin.to_tuple()),'extent':list(bounds.box_extent.to_tuple()),'materials':mats}
 if m.get_name() in ['SM_Rock_1','SM_Rock_4','SM_Rock_8','SM_Rock_12','SM_Rock_20','SM_Rock_28','SM_Small_Rock_2','SM_Jungle_Rock_1']:
  task=unreal.AssetExportTask();task.object=m;task.filename=str(out/(m.get_name()+'.fbx'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.StaticMeshExporterFBX();task.options=unreal.FbxExportOption();row['exported']=unreal.Exporter.run_asset_export_task(task)
 rows.append(row)
(out/'audit.json').write_text(json.dumps(rows,indent=2));RESULT={'meshes':len(rows),'exported':[r['path'] for r in rows if r.get('exported')]}
