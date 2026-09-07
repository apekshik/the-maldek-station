from pathlib import Path
import unreal,json
b=Path(__file__).resolve().parents[1]
old=next(r for r in json.loads((b/'parking/live_before.json').read_text())['actors'] if r['label']=='R12_Forest_Approach_Aligned')['components'][0]['materials'][0]
m=unreal.load_asset('/Game/MaldekRefinement/R12/Parking/Meshes/SM_VF10_Parking_Forest_Connector');m.set_material(0,unreal.load_asset(old));unreal.EditorAssetLibrary.save_loaded_asset(m)
source=(b/'scripts/r13_capture.py').read_text().replace("out=base.parent/'revision13/reviews'","out=base/'parking/reviews'")
exec(compile(source,str(b/'scripts/r13_capture.py'),'exec'))
