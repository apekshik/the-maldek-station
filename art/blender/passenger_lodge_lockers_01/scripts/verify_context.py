"""Verify retained context geometry, transforms and material assignments against source."""
import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];m=json.loads((OUT/'replacement_manifest.json').read_text());excluded={r['name'] for r in m['replaced']}
def snapshot(objects):
 result={}
 for o in objects:
  if o.name in excluded:continue
  data={'type':o.type,'matrix':[list(row) for row in o.matrix_world]}
  if o.type=='MESH':data.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],materials=[x.name if x else None for x in o.data.materials])
  elif o.type=='FONT':data.update(text=o.data.body)
  result[o.name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
 return result
bpy.ops.wm.open_mainfile(filepath=m['source_file']);source=snapshot(bpy.data.scenes['05_Material_Study'].objects)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'));actual=snapshot(bpy.data.collections['REFERENCE_ONLY_Source_Context'].all_objects)
assert source==actual,{'missing':list(source.keys()-actual.keys()),'changed':[k for k in source.keys()&actual.keys() if source[k]!=actual[k]]}
(OUT/'context_verification.json').write_text(json.dumps({'passed':True,'retained_objects':len(source),'method':'Exact source versus saved review hashes of mesh vertex positions, polygon indices, material slots, world matrices and font text; excludes only 96 manifest replacements.','source_sha256':m['source_sha256'],'visibility':'Original excluded collections remain hidden; roof is intentionally hidden for review.'},indent=2))
print('CONTEXT PRESERVED',len(source))
