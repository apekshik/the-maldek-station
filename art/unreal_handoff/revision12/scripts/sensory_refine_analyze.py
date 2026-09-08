"""Offline PCM mixer-output check; does not claim perceptual listening validation."""
import array,json,math,wave,sys
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'sensory_refine'
if len(sys.argv)>1:out=out/sys.argv[1]
with wave.open(str(out/'walking_mix.wav'),'rb') as f:
 assert f.getsampwidth()==2
 values=array.array('h',f.readframes(f.getnframes()))
 peak=max(abs(v) for v in values)/32768
 rms=math.sqrt(sum((v/32768)**2 for v in values)/len(values))
 clipped=sum(abs(v)>=32760 for v in values)
 result={'peak':peak,'rms':rms,'clipped_samples':clipped,'samples':len(values),'seconds':f.getnframes()/f.getframerate()}
(out/'mix_analysis.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
