"""Promote only a saved stage with structural, walking and visual evidence."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];stage=JOB['stage'];assert stage in ['Circulation','Architecture','Infrastructure']
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
ledger=json.loads((b/'integration_ledger.json').read_text());assert ledger['stages'][stage]['imported'] and ledger['stages'][stage]['saved']
audit=json.loads((b/('audit_'+stage.lower()+'.json')).read_text());assert audit['success']
visual=json.loads((b/'reviews'/stage.lower()/'visual_review.json').read_text());assert visual['accepted']
latest={}
for file in JOB['route_reports']:
 report=json.loads((b/file).read_text());assert report['phase']=='finished' and not report.get('error'),file
 for r in report['results']:latest[r['name'],r['direction']]=r
for name in JOB['required_routes']:
 for direction in ['forward','reverse']:assert latest[name,direction]['passed'],(name,direction,latest[name,direction]['reason'])
record={'accepted':True,'scope':stage+' stage only; complete final validation/default-map promotion remains separate.','route_reports':JOB['route_reports'],'routes':[{'name':name,'directions':['forward','reverse']} for name in JOB['required_routes']],'audit':'audit_'+stage.lower()+'.json','visual_review':'reviews/'+stage.lower()+'/visual_review.json','manifest_sha256':hashlib.sha256((b/'handoff_manifest.json').read_bytes()).hexdigest()}
(b/('acceptance_'+stage.lower()+'.json')).write_text(json.dumps(record,indent=2));ledger['stages'][stage]['accepted']=True;(b/'integration_ledger.json').write_text(json.dumps(ledger,indent=2));RESULT=record
