import json,re,sys
from pathlib import Path
b=Path(__file__).resolve().parents[1];variant=sys.argv[1];log=Path(sys.argv[2]).read_text(encoding='utf-8',errors='replace')
start=log.rfind('R12_GPU_PROFILE_BEGIN_'+variant);end=log.find('R12_GPU_PROFILE_END_'+variant,start);assert start>=0 and end>start
text=log[start:end];(b/variant/'gpu_profile.txt').write_text(text,encoding='utf-8');rows=[];queue=None
for line in text.splitlines():
 if 'GPU Profile for Frame' in line:queue=line.split('GPU Profile for Frame',1)[1].strip()
 times=re.findall(r'([\d.]+) ms',line)
 if len(times)==2 and '┃' in line:
  name=line.split('┃')[-2].strip();rows.append({'queue':queue,'event':name,'exclusive_ms':float(times[0]),'inclusive_ms':float(times[1])})
(b/variant/'gpu_profile.json').write_text(json.dumps(rows,indent=2))
for r in sorted(rows,key=lambda r:r['exclusive_ms'],reverse=True)[:20]:print(f"{r['exclusive_ms']:6.3f} / {r['inclusive_ms']:6.3f}  {r['queue']}  {r['event']}")
