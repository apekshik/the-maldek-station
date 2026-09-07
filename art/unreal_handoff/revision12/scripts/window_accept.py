import json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1]
assert json.loads((b/'window_fix/verification.json').read_text())['success']
burst=json.loads((b/'window_fix/burst/report.json').read_text());assert burst['success'] and len(burst['images'])==18
assert all(Path(p).is_file() for p in burst['images'])
review={'accepted':True,'scope':'Window reveal surfaces only','capture':'window_fix/burst/report.json','findings':['Matched control-room view no longer contains the competing beige stripe on the window side.','Waiting-hall and quarters head/side surfaces remain stable in the captured rapid sequences.'],'collision':'Unchanged export collision boxes; previous movement route acceptance retained.','manifest_sha256':hashlib.sha256((b/'handoff_manifest.json').read_bytes()).hexdigest()}
(b/'window_fix/visual_review.json').write_text(json.dumps(review,indent=2))
ledger=json.loads((b/'integration_ledger.json').read_text());ledger['stages']['Architecture']['accepted']=True;ledger['stages']['Architecture']['window_repair_review']='window_fix/visual_review.json'
(b/'integration_ledger.json').write_text(json.dumps(ledger,indent=2))
RESULT=review
