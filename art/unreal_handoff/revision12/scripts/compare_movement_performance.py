"""Compare identical ordinary walking routes; retain hitch counts and percentiles."""
import json,statistics,math
from pathlib import Path
b=Path(__file__).resolve().parents[1]
a=json.loads((b/'baseline/movement_capture.json').read_text());z=json.loads((b/'final/movement_capture.json').read_text())
assert a['success'] and z['success']
for key in ['measurement_version','tests','viewport_size','console_settings','player']:assert a[key]==z[key],key
def stats(rows):
 result={'frames':len(rows)}
 for key in ['frame_ms','game_ms','render_ms','rhi_ms','gpu_ms','draw_calls','process_physical_bytes','streaming_texture_bytes','nonstreaming_texture_bytes','texture_pool_bytes']:
  values=sorted(r[key] for r in rows if key in r)
  if key in ['render_ms','rhi_ms'] and not any(v>0 for v in values):
   result.setdefault('unavailable_counters',[]).append(key);continue
  if values:result[key]={'mean':statistics.mean(values),'p95':values[math.ceil(len(values)*.95)-1],'p99':values[math.ceil(len(values)*.99)-1],'max':values[-1]}
 result['mean_fps']=1000/result['frame_ms']['mean']
 result['frames_over_33ms']=sum(r['frame_ms']>33.333 for r in rows)
 result['hitches_over_50ms']=[{'point':r['point'],'elapsed_seconds':r['elapsed_seconds'],'frame_ms':r['frame_ms'],'gpu_ms':r.get('gpu_ms')} for r in rows if r['frame_ms']>50]
 return result
report={'scope':'Same retained forest and bridge paths, both directions, actual walking capsule, 2560x1440, existing production night/weather settings, no frame generation.','routes':[],'regressions':[]}
for old,new in zip(a['results'],z['results']):
 assert (old['name'],old['direction'])==(new['name'],new['direction'])
 x,y=stats(old['performance']),stats(new['performance'])
 delta={key:100*(y[key]['mean']/x[key]['mean']-1) for key in ['frame_ms','gpu_ms','game_ms','draw_calls','process_physical_bytes'] if x.get(key,{}).get('mean',0)>0}
 report['routes'].append({'name':old['name'],'direction':old['direction'],'baseline':x,'r12':y,'percent_change':delta})
 for key in ['frame_ms','gpu_ms']:
  if delta[key]>10:report['regressions'].append({'name':old['name'],'direction':old['direction'],'metric':key,'percent':delta[key]})
report['baseline_meets_mean_60fps']=all(r['baseline']['mean_fps']>=60 for r in report['routes'])
report['r12_meets_mean_60fps']=all(r['r12']['mean_fps']>=60 for r in report['routes'])
report['accepted']=report['r12_meets_mean_60fps'] and not report['regressions']
(b/'movement_performance_comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='routes'},indent=2))
