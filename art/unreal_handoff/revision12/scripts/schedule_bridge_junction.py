"""Resolve observed circulation dependency without changing the approved geometry."""
import json
from pathlib import Path
base=Path(__file__).resolve().parents[1];p=base/'handoff_manifest.json';m=json.loads(p.read_text());changed=[]
for r in m['chunks']:
 if r['collection']=='20_Lookout_Bridge':r['stage']='Circulation';changed.append(r['name'])
p.write_text(json.dumps(m,indent=2))
(base/'bridge_stage_dependency.json').write_text(json.dumps({'assemblies':changed,'reason':'Actual Unreal player blocked by the superseded R11 bridge-junction guard at x=15,y=6.7. Bring the pre-audited retained-span/new-junction assembly into circulation before accepting routes. No geometry or transforms changed.','source_preservation_report':'bridge_source_preservation.json'},indent=2))
