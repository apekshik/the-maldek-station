import json,numpy as np
from pathlib import Path
b=Path(__file__).resolve().parents[1]/'trim2'
def read(name):
 d=json.loads((b/name).read_text());assert d['success'];out={}
 for r in d['results']:
  a=r['camera_samples'];z=np.array([x['eye_z'] for x in a]);body=np.array([x['capsule_z'] for x in a])
  out[r['name']+'/'+r['direction']]={'camera_height_second_difference_p95_cm':float(np.percentile(np.abs(np.diff(z,n=2)),95)),'capsule_height_second_difference_p95_cm':float(np.percentile(np.abs(np.diff(body,n=2)),95)),'falling_frames':sum(x['falling'] for x in a),'passed':r['passed']}
 return out
before=read('stairs_full_before.json');after=read('stairs_full_after.json');rows=[]
for k in before:
 reduction=1-after[k]['camera_height_second_difference_p95_cm']/after[k]['capsule_height_second_difference_p95_cm']
 rows.append({'route':k,'before':before[k],'after':after[k],'same_frame_camera_vs_capsule_reduction_percent':round(100*reduction,1)})
r={'routes':rows,'measurement':'Per-frame height second difference: camera versus capsule on identical frames within each run, with full walking input. This measures suppression of step discontinuities, not physical acceleration or subjective comfort. Quantized Windows clock timestamps are not used to estimate acceleration.','success':all(x['after']['passed'] and x['after']['falling_frames']==0 for x in rows)}
(b/'stair_comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
