"""Paired fixed-camera timings. Missing counters are never treated as measured zero."""
import json,statistics,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];before=json.loads((b/'baseline/performance_capture.json').read_text());after=json.loads((b/'final/performance_capture.json').read_text())
assert before['success'] and after['success']
for key in ['measurement_version','viewport_size','console_settings','environment','cameras','pawn_settings']:assert before[key]==after[key],('Unpaired benchmark',key)
def percentile(values,p):
 v=sorted(values);return v[min(len(v)-1,math.ceil(len(v)*p)-1)]
def summarize(rows):
 result={'samples':len(rows)}
 for key in ['frame_ms','game_ms','render_ms','rhi_ms','gpu_ms','draw_calls','process_physical_bytes','streaming_texture_bytes','nonstreaming_texture_bytes','texture_pool_bytes']:
  values=[r[key] for r in rows if key in r]
  if key in ['render_ms','rhi_ms'] and not any(v>0 for v in values):
   result.setdefault('unavailable_counters',[]).append(key);continue
  if values:result[key]={'mean':statistics.mean(values),'p95':percentile(values,.95),'p99':percentile(values,.99),'max':max(values)}
 result['mean_fps']=1000/result['frame_ms']['mean'];result['frames_over_33ms']=sum(r['frame_ms']>33.333 for r in rows)
 result['hitches_over_50ms']=[{'sample_index':i,'frame_ms':r['frame_ms'],'game_ms':r.get('game_ms'),'gpu_ms':r.get('gpu_ms')} for i,r in enumerate(rows) if r['frame_ms']>50]
 return result
report={'hardware':'RTX 5070 Ti, 16 GB','output_resolution':[2560,1440],'frame_generation':False,'scope':'Identical six fixed camera viewpoints and engine settings in initialized production Snow/night PIE. Engine counters measure real rendered frames.','counter_notes':'Raw game-thread timing can include waiting. All-zero render/RHI counters are unavailable, not zero-cost work. Texture residency is not total device VRAM usage.','settings':before['console_settings'],'cameras':{},'regressions':[]}
for name in sorted({r['camera'] for r in before['samples']}):
 a=summarize([r for r in before['samples'] if r['camera']==name]);z=summarize([r for r in after['samples'] if r['camera']==name]);delta={k:100*(z[k]['mean']/a[k]['mean']-1) for k in ['frame_ms','game_ms','gpu_ms','draw_calls','process_physical_bytes','streaming_texture_bytes'] if a.get(k,{}).get('mean',0)>0}
 report['cameras'][name]={'baseline':a,'r12':z,'percent_change':delta}
 for key in ['frame_ms','gpu_ms']:
  if delta[key]>10:report['regressions'].append({'camera':name,'metric':key,'percent':delta[key]})
report['baseline_meets_mean_60fps']=all(r['baseline']['mean_fps']>=60 for r in report['cameras'].values())
report['r12_meets_mean_60fps']=all(r['r12']['mean_fps']>=60 for r in report['cameras'].values())
report['accepted']=report['r12_meets_mean_60fps'] and not report['regressions']
(b/'performance_comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='cameras'},indent=2))
