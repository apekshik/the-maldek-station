"""Final independent routes using surveyed aisle waypoints."""
import json,time
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
routes=json.loads((repo/'art/blender/visual_fidelity_07/layout.json').read_text())['routes'];r={x['name']:x['points'] for x in routes}
forest=[[-35,-60.5,-1],[-35,-57.5,-1]]+json.loads((b/'forest_arrival_alignment.json').read_text())['path']+[[-13.5,-17.8,0],[-13.5,-16.35,0],[-14.01,-16.35,0]]
bridge=[[12,6.7,4]]+json.loads((b.parent/'revision11/layout.json').read_text())['bridge_points']+[[19,33,4]]
aisles=[
 {'name':'Control interior aisle','points':[[-3.3,-.8,4],[-3.3,-2.6,4],[-6.5,-2.6,4],[-6.5,-3.5,4],[-4,-3.5,4]]},
 {'name':'Generator clear entrance','points':[[30,-10.6,-1],[30,-12.4,-1],[31.5,-12.4,-1],[31.5,-15.5,-1]]},
 {'name':'Workshop shared west door','points':[[31.5,-15.5,-1],[32.5,-15.5,-1],[34.3,-15.5,-1]]},
 {'name':'Water terrace access','points':[[22,-12,-.7],[21.5,-13.5,-.85],[21,-15,-1],[21,-15.7,-1],[19,-15.7,-1]]}]
# Retain successfully surveyed room paths from the architecture request's samples.
previous=json.loads((b/'routes_architecture.json').read_text())
for name in ['Waiting hall interior','Quarters interior','Relay interior']:
 row=next(x for x in previous['results'] if x['name']==name and x['direction']=='forward');assert row['passed']
 # Sampled feet positions are actual walkable paths; decimate to roughly 0.5 m.
 points=[]
 for s in row['samples']:
  p=[s['p'][0],s['p'][1],s['feet_z']]
  if not points or sum((p[i]-points[-1][i])**2 for i in range(2))>.25:points.append(p)
 aisles.append({'name':name,'points':points})
extra=[{'name':'Forest to arrival','points':forest},{'name':'Entire lookout bridge','points':bridge}]+aisles
(b/'final_route_definitions.json').write_text(json.dumps({'approved_routes':routes,'extra_routes':extra},indent=2))
job={'id':'full-routes-'+str(time.time_ns()),'script':'run_routes.py','stage':'Full','report':'routes_full.json','extra_routes':extra}
(b/'request.json').write_text(json.dumps(job))
