"""Compose approved routes into one ordinary walk, with no resets between destinations."""
import json,time
from pathlib import Path
b=Path(__file__).resolve().parents[1];d=json.loads((b/'final_route_definitions.json').read_text());r={x['name']:x['points'] for x in d['approved_routes']+d['extra_routes']};tour=[]
def add(points):
 for p in points:
  if not tour or sum((p[i]-tour[-1][i])**2 for i in range(3))>.0025:tour.append(p)
def route(name,reverse=False):add(r[name][::-1] if reverse else r[name])
route('Forest to arrival');route('Arrival');route('Arrival turn onto platform');add([[-13.15,-14.3,4]])
route('Completed rear hall approach');route('Waiting hall interior');add([[-10.25,2.7,4]])
route('Control front approach');route('Control interior aisle');route('Control interior aisle',True);route('Control front approach',True)
add([[-10.25,2.7,4]]);route('Waiting hall interior',True);route('Completed rear hall approach',True)
add([[-13.15,-11.8,4],[-1.5,-11.8,4],[-1.5,-12.2,4]])
route('Quarters lower approach');route('Quarters');route('Quarters landing and doorway');route('Quarters interior')
route('Quarters interior',True);route('Quarters landing and doorway',True);route('Quarters',True);route('Quarters lower approach',True)
add([[-13.15,-12.2,4],[-13.15,-8.1,4],[-13.15,-7.4,4]]);route('Waiting hall interior');add([[-10.25,2.7,4],[4.5,2.7,4]])
route('Boarding threshold');route('Boarding threshold',True);add([[4.5,4.5,4],[4.5,7.5,4],[7,7.5,4]])
route('Internal descending stair',True);add([[7,-.5,0],[12,-6.7,0]])
route('Service descent lower exit',True);route('Exterior_service');route('Exterior_service',True);route('Service descent lower exit')
generator_aisle=[[27,-15,-1],[27.42,-15,-1],[27.42,-14.4,-1],[27.52,-14.05,-1],[28.4,-13.75,-1],[31.5,-13.75,-1],[31.5,-15.5,-1]]
add([[18,-6.7,0]]);route('Service_road');add(generator_aisle)
route('Workshop shared west door');route('Workshop shared west door',True);add(generator_aisle[::-1])
route('Service_road',True)
# Water terrace is an out-and-back from the surveyed service road bend.
add(r['Service_road'][:21]);route('Water terrace access');route('Water terrace access',True);add(r['Service_road'][:21][::-1])
add([[18,-3,0]]);route('Relay_outbound');add([[48,12.5,3]]);route('Relay interior',True);route('Relay_return')
add([[16.25,6.7,4]]);route('Entire lookout bridge')
record={'name':'Continuous station tour','points':tour,'destinations':['parking','forest','sideways arrival','waiting hall','control room','quarters','gondola threshold','internal service stair','external service stair','generator','workshop','water terrace','relay loop','entire lookout bridge']}
(b/'continuous_route_definition.json').write_text(json.dumps(record,indent=2))
(b/'request.json').write_text(json.dumps({'id':'continuous-'+str(time.time_ns()),'script':'run_routes.py','stage':'Full','report':'routes_continuous.json','names':[record['name']],'extra_routes':[record]}))
