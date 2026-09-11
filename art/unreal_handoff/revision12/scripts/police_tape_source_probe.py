import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];mesh=unreal.load_asset('/Game/Megaplant_Library/Tree_European_Beech/Tree_European_Beech_01/SK_European_Beech_01_B');r={}
try:r['source_files']=mesh.get_editor_property('asset_import_data').extract_filenames()
except Exception as e:r['source_error']=str(e)
t=unreal.AssetExportTask();t.object=mesh;t.filename=str(b/'police_tape/wrap_fit/source_probe.fbx');t.automated=True;t.prompt=False;t.replace_identical=True;t.exporter=unreal.SkeletalMeshExporterFBX();opt=unreal.FbxExportOption();opt.set_editor_property('export_source_mesh',True);opt.set_editor_property('level_of_detail',False);t.options=opt;r['export']=unreal.Exporter.run_asset_export_task(t);(b/'police_tape/wrap_fit/source_probe.json').write_text(json.dumps(r));RESULT=r
