import unreal,json
from pathlib import Path
lib=unreal.EditorAssetLibrary;sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);r={}
for i in range(3):
 mesh=lib.load_asset('/Game/MaldekRefinement/R06/Meshes/SM_R06_Pine_'+str(i));settings=[]
 for percent,screen in [(1.,1.),(.45,.35),(.16,.15),(.05,.06)]:settings.append(unreal.EditorScriptingMeshReductionSettings(percent_triangles=percent,screen_size=screen))
 options=unreal.EditorScriptingMeshReductionOptions(auto_compute_lod_screen_size=False,reduction_settings=settings)
 r[str(i)]=sub.set_lods(mesh,options);lib.save_loaded_asset(mesh)
(Path(__file__).resolve().parents[1]/'revision06/tree_lods.json').write_text(json.dumps(r))
