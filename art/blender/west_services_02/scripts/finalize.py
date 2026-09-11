import json,hashlib
from pathlib import Path
p=Path('art/blender/west_services_02')
r=json.loads((p/'verification.json').read_text());d=json.loads((p/'delivery.json').read_text());h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert r['passed'] and d['sha256']==h(p/d['blend'])
assert len(list((p/'previews').glob('*.png')))==12
hits=json.loads((p/'roof_interface_probe.json').read_text());assert hits==[['WSE_Riser_standoff.003','WS_Gable'],['WSE_Riser_standoff.004','WS02_StandoffRoofSocket']]
d.update({'scene':'Station_West_Services_Integrated','package_objects':r['package_counts'],'route_samples':sum(x['samples'] for x in r['routes']),'routes_passed':len(r['routes']),'roof_interfaces_passed':True,'previews':{f.name:h(f) for f in sorted((p/'previews').glob('*.png'))},'limitations':'Blender assembly only. Unreal import, live terrain fit, materials/export/collision remain separate.'})
(p/'delivery.json').write_text(json.dumps(d,indent=2))
print(json.dumps({k:d[k] for k in ['blend','sha256','verification_passed','route_samples','routes_passed','roof_interfaces_passed']},indent=2))
