import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';lib=unreal.EditorAssetLibrary
mesh=lib.load_asset('/Game/MaldekRefinement/R11/Meshes/SM_R04_21_Maintenance')
for i,s in enumerate(mesh.static_materials):
 if str(s.material_slot_name)=='R03_Wet_Gravel':mesh.set_material(i,lib.load_asset('/Game/MaldekRefinement/R05/Materials/M_R03_Wet_Gravel'))
lib.save_loaded_asset(mesh)
runpy.run_path(str(Path(__file__).with_name('style_r11.py')))
