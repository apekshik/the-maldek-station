import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];rows=[]
for path in ['/Game/MaldekRefinement/ForestTest/Meshes/SM_ForestTerrain','/Game/MaldekRefinement/R12/Meshes/SM_R12_Terrain']:
 mesh=unreal.load_asset(path);ns=mesh.get_editor_property('nanite_settings')
 rows.append({'mesh':path,'nanite':str(ns),'collision':str(mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')),'materials':[str(s.material_interface.get_path_name()) for s in mesh.static_materials]})
(b/'terrain_render_audit.json').write_text(json.dumps(rows,indent=2));RESULT=rows
