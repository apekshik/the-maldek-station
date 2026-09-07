"""Paired walking paths confined to retained forest and bridge geometry."""
import json,time,sys
from pathlib import Path
b=Path(__file__).resolve().parents[1]
variant=sys.argv[1];assert variant in ['baseline','final']
d=json.loads((b/'final_route_definitions.json').read_text())
forest=next(r['points'] for r in d['extra_routes'] if r['name']=='Forest to arrival')
routes=[{'name':'Retained forest walking benchmark','points':forest[30:67]},
        {'name':'Retained bridge walking benchmark','points':[[16,15,4],[17,20.37,4],[18,25.74,4],[19,31.12,4]]}]
job={'id':'walk-benchmark-'+str(time.time_ns()),'script':'run_routes.py','benchmark':True,'stage':'Benchmark','report':variant+'/movement_capture.json','extra_routes':routes,'names':[r['name'] for r in routes]}
(b/'request.json').write_text(json.dumps(job))
