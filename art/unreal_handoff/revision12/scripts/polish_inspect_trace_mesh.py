import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];mesh=unreal.load_asset('/Game/MaldekRefinement/R12/Meshes/SM_R12_VF06_Waiting_Hall_010_solid')
ns=mesh.get_editor_property('nanite_settings');rt=mesh.get_editor_property('ray_tracing_proxy_settings')
report={'nanite':str(ns),'ray_tracing_proxy':str(rt),'mesh_methods':[s for s in dir(mesh) if any(k in s for k in ['triangle','lod','build','nanite'])],'subsystem_methods':[s for s in dir(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)) if any(k in s for k in ['triangle','lod','build','nanite'])]}
report['triangles']=mesh.get_num_triangles(0);report['set_nanite_doc']=unreal.StaticMeshEditorSubsystem.set_nanite_settings.__doc__
(b/'polish'/'trace_mesh_audit.json').write_text(json.dumps(report,indent=2));RESULT=report
