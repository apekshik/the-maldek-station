import unreal,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];rows=json.loads((base/'handoff_manifest.json').read_text())['chunks'];name=JOB['name'];r=next(r for r in rows if r['name']==name);m=unreal.load_asset('/Game/MaldekRefinement/R12/Meshes/'+name)
b=m.get_bounds();vec=lambda v:[v.x,v.y,v.z]
RESULT={'name':name,'actual':[vec(b.origin-b.box_extent),vec(b.origin+b.box_extent)],'expected_source_bounds':r['bounds'],'sources':r['sources'],'collision_sources':[c['source'] for c in r['collision_boxes']],'nanite':str(m.get_editor_property('nanite_settings'))}
(base/'import_diagnostic.json').write_text(json.dumps(RESULT,indent=2))
