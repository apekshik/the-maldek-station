import json,time
from pathlib import Path
b=Path(__file__).resolve().parents[1];layout=json.loads((b.parents[2]/'art/blender/visual_fidelity_07/layout.json').read_text())
names=[r['name'] for r in layout['routes'] if r['name'] not in ['Completed rear hall approach','Quarters landing and doorway','Control front approach','Boarding threshold']]+['Forest to arrival','Entire lookout bridge']
(b/'request.json').write_text(json.dumps({'id':'accept-circulation-'+str(time.time_ns()),'script':'accept_stage.py','stage':'Circulation','route_reports':['routes_circulation.json','routes_junction.json','routes_forest_alignment.json'],'required_routes':names}))
