"""Resolve a finite reviewed fixture list to exact component identities before import."""
import json
from pathlib import Path
b=Path(__file__).resolve().parents[1]
p=b/'handoff_manifest.json';m=json.loads(p.read_text())
inventory={r['label']:r for r in json.loads((b/'replacement_inventory.json').read_text())}
for t in m['retire_components']:
 t.setdefault('stage','Architecture' if 'Doors_' in t['actor'] else 'Circulation')
labels=[prefix+part for prefix in ['R08_Control_Entry_','R08_Waiting_Hall_Entry_'] for part in ['Backplate','Housing','Hood','Diffuser','Guard_Left','Guard_Right','Guard_Crossbar','Conduit']]
rows=[]
for label in labels:
 r=inventory[label];assert len(r['components'])==1
 c=r['components'][0]
 t={'actor':r['r12_path'],'component':c['name'],'old_mesh':c['mesh'],'stage':'Infrastructure','reason':'Superseded by approved VF06 bulkhead assembly; original actor identity and functional light retained.'}
 rows.append(dict(label=label,**t))
 if not any(x['actor']==t['actor'] and x['component']==t['component'] for x in m['retire_components']):m['retire_components'].append(t)
p.write_text(json.dumps(m,indent=2))
(b/'fixture_replacement_manifest.json').write_text(json.dumps({'components':rows,'preserved':'Existing canopy fixtures, generator west entrance, fuel yard exit and lookout lights remain. Only the enumerated duplicate entry fixture components are retired.'},indent=2))
