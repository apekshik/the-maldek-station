"""Revalidate saved stages after reviewed local export repairs; final promotion remains gated."""
import json,runpy
from pathlib import Path
b=Path(__file__).resolve().parents[1]
visual=json.loads((b/'final_visual_review.json').read_text());assert visual['accepted']
summary=json.loads((b/'independent_route_summary.json').read_text());assert summary['passed'] and summary['directional_tests']==54
names=sorted({r['name'] for r in summary['routes']});results={}
for stage in ['Circulation','Architecture','Infrastructure']:
 runpy.run_path(str(b/'scripts/audit_stage.py'),init_globals={'JOB':{'stage':stage}})
 p=b/'reviews'/stage.lower();p.mkdir(parents=True,exist_ok=True)
 (p/'visual_review.json').write_text(json.dumps({'accepted':True,'scope':stage+' in the integrated station.','final_review':'final_visual_review.json','review':visual},indent=2))
 results[stage]=runpy.run_path(str(b/'scripts/accept_stage.py'),init_globals={'JOB':{'stage':stage,'route_reports':['routes_full.json','routes_junction_repairs.json'],'required_routes':names}})['RESULT']
RESULT={'accepted_stages':list(results),'remaining':'Continuous tour, editor reopen, package and performance/default-map promotion gates.'}
