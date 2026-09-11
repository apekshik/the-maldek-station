"""Local Python: prepare ordinary capsule walks through the changed trailhead."""
import json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';plan=json.loads((out/'plan.json').read_text());old=json.loads((out/'source_audit.json').read_text())[0]['vertices']
rest=[[(old[i][j]+old[i+1][j])/2 for j in range(3)] for i in range(34,len(old),2)]
centre=plan['centreline'];route=[[-35,-60.5,-1],[-34,-57,-1],[-32,-54,-1]]+centre+rest
routes=[{'name':'Parking to station path','points':route}]
for side in [-1,1]:
 points=[[p[0]+side*.75,p[1],p[2]] for p in centre]
 routes.append({'name':'Trailhead '+('left' if side<0 else 'right')+' clearance','points':[[points[0][0],-54,-1]]+points})
routes.append({'name':'Bays to trailhead','points':[[-43,-56,-1],[-38,-55,-1],[-34,-54,-1],[-32,-53,-1]]+centre})
job={'id':'parking-navigation-walks','script':'run_routes.py','names':[r['name'] for r in routes],'extra_routes':routes,'report':'parking_navigation/routes.json'}
(out/'walk_job.json').write_text(json.dumps(job,indent=2));(b/'request.json').write_text(json.dumps(job))
