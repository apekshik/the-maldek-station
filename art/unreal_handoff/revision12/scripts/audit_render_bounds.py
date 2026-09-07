"""Record bounds of rendered triangle vertices, excluding orphaned source vertices."""
import bpy,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1];path=base/'handoff_manifest.json';manifest=json.loads(path.read_text())
bpy.ops.wm.open_mainfile(filepath=str(base/'VF07_R12_Export.blend'),load_ui=False)
changes=[]
for row in manifest['chunks']:
 o=bpy.data.objects[row['name']];used={i for p in o.data.polygons for i in p.vertices};vertices=[o.matrix_world@o.data.vertices[i].co for i in used]
 render_bounds=[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]]
 error=max(abs(render_bounds[j][i]-row['bounds'][j][i]) for j in range(2) for i in range(3))
 if error>.0001:
  changes.append({'name':row['name'],'orphan_vertices':len(o.data.vertices)-len(used),'old_bounds':row['bounds'],'render_bounds':render_bounds,'difference_m':error})
  row['unreferenced_vertex_bounds']=row['bounds'];row['bounds']=render_bounds
path.write_text(json.dumps(manifest,indent=2));(base/'render_bounds_audit.json').write_text(json.dumps({'changes':changes,'geometry_modified':False},indent=2));print(json.dumps(changes,indent=2))
