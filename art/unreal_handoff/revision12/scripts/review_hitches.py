"""Record observed outliers; distinguish GPU work from unexplained wall-clock stalls."""
import json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1]
outliers=[];counts={};hashes={}
for stage in ['baseline','final']:
 for kind in ['performance','movement']:
  path=b/stage/(kind+'_capture.json');d=json.loads(path.read_text());assert d['success']
  hashes[str(path.relative_to(b))]=hashlib.sha256(path.read_bytes()).hexdigest()
  groups=[('fixed views',d['samples'])] if kind=='performance' else [(r['name']+' '+r['direction'],r['performance']) for r in d['results']]
  counts[stage+'/'+kind]=sum(len(rows) for _,rows in groups)
  for group,rows in groups:
   for i,r in enumerate(rows):
    if r['frame_ms']>33.333:outliers.append({'stage':stage,'capture':kind,'group':group,'sample_index':i,'sample':r})
assert not any(r['sample']['frame_ms']>50 for r in outliers)
report={'accepted':True,'capture_hashes':hashes,'sample_counts':counts,'outliers_over_33ms':outliers,'hitches_over_50ms':0,
 'review':'Two isolated R12 outliers: 39.17 ms at the service view and 42.28 ms on reverse forest walking, point 14 at 6.688 seconds. Their GPU times were 9.42 and 9.22 ms and game-thread counters 11.58 and 14.07 ms, so these do not demonstrate a GPU workload stall. No repeated >33 ms clusters or >50 ms samples occurred in these captures. Baseline also has isolated >33 ms frames. The exact source of the wall-clock outliers is unproven; they are retained rather than filtered. p95/p99 results remain in the paired reports. This finite sample is not a guarantee of hitch-free play.'}
(b/'hitch_review.json').write_text(json.dumps(report,indent=2));print(json.dumps({'counts':counts,'outliers':len(outliers),'over_50ms':0}))
