"""Match ray-traced geometry to visible door/window trim without changing collision."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];m=json.loads((b/'handoff_manifest.json').read_text());rows=[]
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
for c in m['chunks']:
 names=[s.lower() for s in c['sources']]
 if not c['nanite'] or not any(any(k in s for k in ['sill','threshold','jamb','window_frame','door_frame','door_return','window_return','door_lintel']) for s in names):continue
 mesh=unreal.load_asset('/Game/MaldekRefinement/R12/Meshes/'+c['name']);ns=mesh.get_editor_property('nanite_settings')
 before={'fallback_relative_error':ns.fallback_relative_error,'fallback_percent_triangles':ns.fallback_percent_triangles,'fallback_target':str(ns.fallback_target),'triangles':mesh.get_num_triangles(0)}
 ns.set_editor_property('fallback_relative_error',0.0);ns.set_editor_property('fallback_percent_triangles',1.0);ns.set_editor_property('fallback_target',unreal.NaniteFallbackTarget.PERCENT_TRIANGLES)
 unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).set_nanite_settings(mesh,ns,True);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 c['nanite_fallback_relative_error']=0.0;c['nanite_fallback_percent_triangles']=1.0
 c['nanite_fallback_target']='PERCENT_TRIANGLES'
 rows.append({'mesh':c['name'],'triangles':c['triangles'],'before':before,'after':{'fallback_relative_error':0,'fallback_percent_triangles':1,'fallback_target':'PERCENT_TRIANGLES','triangles':mesh.get_num_triangles(0)}})
assert rows
(b/'handoff_manifest.json').write_text(json.dumps(m,indent=2))
(b/'polish'/'trim_fallback_repair.json').write_text(json.dumps({'success':True,'meshes':rows,'reason':'Close sill artifacts disappear with hardware Lumen disabled; repair simplified trace geometry locally instead of disabling lighting globally.','collision_and_source_geometry_changed':False},indent=2));RESULT={'meshes':len(rows),'triangles':sum(r['triangles'] for r in rows)}
