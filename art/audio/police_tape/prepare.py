import soundfile as sf,numpy as np,json,hashlib
from scipy.signal import resample_poly
from pathlib import Path
p=Path(__file__).resolve().parent;(p/'wav').mkdir(exist_ok=True);x,sr=sf.read(p/'originals/tearing_duct_tape.mp3');x=x.mean(axis=1);rows=[]
for i,(start,end) in enumerate([(8,9.6),(17.7,19.2),(25.8,27.6)],1):
 a=x[int(start*sr):int(end*sr)];a-=a.mean();active=np.flatnonzero(abs(a)>.025);lo=max(0,int(active[0]) - int(.01*sr));hi=min(len(a),int(active[-1])+int(.07*sr));a=a[lo:hi];a=resample_poly(a,160,147);gain=.72/max(abs(a));a*=gain;n=192;a[:n]*=np.linspace(0,1,n);n=min(720,len(a));a[-n:]*=np.linspace(1,0,n);name=f'Tape_Tear_{i:02}';file=p/'wav'/f'{name}.wav';sf.write(file,a,48000,subtype='PCM_16');rows.append({'asset':name,'source_range_s':[start+lo/sr,start+hi/sr],'duration_s':len(a)/48000,'peak':float(max(abs(a))),'rms':float(np.sqrt(np.mean(a*a))),'gain':float(gain),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(p/'edits.json').write_text(json.dumps({'processing':'Recorded excerpts only: trim, mono 48kHz PCM16, DC removal, constant peak gain, short edge fades. No synthesis.','clips':rows},indent=2));print(rows)
