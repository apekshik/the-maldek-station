import json,time
from pathlib import Path
b=Path(__file__).resolve().parents[1]
forest=[[-36,-60.5,-1]]+json.loads((b.parent/'revision10/approach_path.json').read_text())['points']+[[-13.5,-16.35,0],[-14.01,-16.35,0]]
bridge=[[12,6.7,4]]+json.loads((b.parent/'revision11/layout.json').read_text())['bridge_points']+[[19,33,4]]
job={'id':'junction-routes-'+str(time.time_ns()),'script':'run_routes.py','names':['East terrace grating','Forest to arrival','Entire lookout bridge'],'extra_routes':[{'name':'Forest to arrival','points':forest},{'name':'Entire lookout bridge','points':bridge}],'report':'routes_junction.json'}
if (b/'forest_arrival_alignment.json').exists():
 forest=[[-35,-60.5,-1],[-35,-57.5,-1]]+json.loads((b/'forest_arrival_alignment.json').read_text())['path']+[[-13.5,-17.8,0],[-13.5,-16.35,0],[-14.01,-16.35,0]]
 job.update(names=['Forest to arrival'],extra_routes=[{'name':'Forest to arrival','points':forest}],report='routes_forest_alignment.json')
(b/'request.json').write_text(json.dumps(job))
