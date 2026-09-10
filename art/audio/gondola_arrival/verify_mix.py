"""Measure captured mixer output, not merely source wave amplitudes."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
p=Path(__file__).resolve().parent;rows=[]
for path in sorted((p/'runtime').glob('*_mix.wav')):
 x,s=sf.read(path,always_2d=True);peak=float(abs(x).max());rms=float(np.sqrt(np.mean(x*x)))
 clipped=int(np.count_nonzero(abs(x)>=.999));frames=int(s*.1)
 windows=[float(np.sqrt(np.mean(x[i:i+frames]**2))) for i in range(0,len(x),frames)]
 rows.append(dict(file=path.name,duration=len(x)/s,peak=peak,rms=rms,clipped_samples=clipped,loudest_100ms_rms=max(windows)))
 assert peak>.05 and rms>.002,(path,'silent/too quiet',peak,rms)
 assert clipped==0,(path,'clipping',clipped)
assert len(rows)==4,rows
(p/'runtime/mix_verification.json').write_text(json.dumps({'success':True,'clips':rows},indent=2));print(json.dumps(rows,indent=2))
