"""Reuse the revision 03 route samples, evaluating modifiers and new detail meshes."""
import bpy, json, math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
BASE=OUT.parent/'revision_03'
source=(BASE/'scripts/validate.py').read_text()
source=source.replace("OUT=Path(__file__).resolve().parents[1]",f"OUT=Path({str(OUT)!r}); BASE=Path({str(BASE)!r})")
source=source.replace("(OUT/'route_points.json')","(BASE/'route_points.json')").replace("(OUT/'blockout_dimensions.json')","(BASE/'blockout_dimensions.json')")
source=source.replace("o.get('collision') or o.name=='Terrain_Cliff_And_Relay_Spur'", "o.get('collision') or o.name=='Terrain_Cliff_And_Relay_Spur' or (o.name.startswith('R04_') and o.get('export_geometry') and 'Glass' not in o.name)")
source=source.replace("for o in colliders:\n    offset=len(verts);verts += [o.matrix_world@v.co for v in o.data.vertices]\n    for p in o.data.polygons: faces.append(tuple(offset+i for i in p.vertices));face_names.append(o.name)","""deps=bpy.context.evaluated_depsgraph_get()
for o in colliders:
    evaluated=o.evaluated_get(deps); me=evaluated.to_mesh()
    offset=len(verts);verts += [o.matrix_world@v.co for v in me.vertices]
    for p in me.polygons: faces.append(tuple(offset+i for i in p.vertices));face_names.append(o.name)
    evaluated.to_mesh_clear()""")
source=source.replace("passed sampled geometry; no revision03 FBX exports or UE5 playtest", "passed evaluated geometry samples; decorative meshes included except glass; no UE5 playtest")
exec(compile(source,str(BASE/'scripts/validate.py'),'exec'))
stats={}
deps=bpy.context.evaluated_depsgraph_get()
for c in ['12_Gondola','02_Control_Room','04_Lower_Drive','01_Upper_Platform']:
 objs=[o for o in bpy.data.collections[c].objects if o.type=='MESH' and not o.hide_render]
 triangles=0
 for o in objs:
  e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);e.to_mesh_clear()
 stats[c]={'visible_mesh_objects':len(objs),'evaluated_triangles':triangles}
(OUT/'mesh_statistics.json').write_text(json.dumps(stats,indent=2))
print('REFINEMENT_STATISTICS',json.dumps(stats),flush=True)
