import bpy,bmesh,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];m=json.loads((b/'handoff_manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(b/'VF07_R12_Export.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for chunk in m['chunks']:
 if chunk['role']!='glass':continue
 for name in chunk['sources']:
  obj=bpy.data.objects.get(name);assert obj,name
  mesh=obj.evaluated_get(dg).to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
  rows.append({'object':name,'assembly':chunk['name'],'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)})
  bm.free();obj.evaluated_get(dg).to_mesh_clear()
report={'objects':rows,'all_closed':all(r['non_manifold_edges']==0 for r in rows)}
(b/'glass_topology.json').write_text(json.dumps(report,indent=2));print(json.dumps({'objects':len(rows),'all_closed':report['all_closed'],'open_objects':[r for r in rows if r['non_manifold_edges']]}))
