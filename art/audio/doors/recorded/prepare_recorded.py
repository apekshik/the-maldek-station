"""Edit downloaded CC0 recordings. No synthesis, artificial noise or generated layers.
Requires numpy, scipy, soundfile (with MP3 decoding). Original pitch is retained.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfiltfilt,resample_poly

base=Path(__file__).resolve().parents[1]
out=base/'wav';out.mkdir(exist_ok=True);sr=48000
sources={s['id']:s for s in json.loads((base/'recorded/sources.json').read_text())}
recordings={}
for ident,s in sources.items():
 p=base/'recorded'/s['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 x,rate=sf.read(p);x=x.mean(axis=1) if x.ndim==2 else x
 if rate!=sr:
  g=math.gcd(rate,sr);x=resample_poly(x,sr//g,rate//g)
 recordings[ident]=x

# Real intercom key presses and answer tone; recorded hardware fault buzzer;
# hotel deadbolt and metal access-door foley. Excerpts are sound-design proxies.
specs=[
 ('KeyPress',828113,.135,.255,.42,350,False),
 ('KeyClear',828113,.750,.905,.42,350,False),
 ('KeyConfirm',828113,16.280,16.670,.36,500,False),
 ('KeyReject',167848,1.490,2.030,.36,350,False),
 ('DoorUnlatch',336660,2.535,2.990,.50,65,False),
 ('DoorMovement',700682,.120,1.700,.38,85,True),
 ('DoorClosingMovement',700705,.120,1.680,.38,85,True),
 ('DoorClose',336660,8.795,9.670,.55,55,False),
 ('DoorUnlock',494128,.240,.691,.48,90,False),
 ('DoorLock',494128,.355,.691,.48,90,False),
]
report={};clips=[]
for name,ident,start,end,peak,cut,loop in specs:
 x=recordings[ident][int(start*sr):int(end*sr)].copy();assert len(x)>1000
 x=sosfiltfilt(butter(2,cut,fs=sr,btype='highpass',output='sos'),x);x-=x.mean()
 if loop:
  n=int(.045*sr);blend=np.linspace(0,1,n)
  seam=x[-n:]*(1-blend)+x[:n]*blend;x=np.concatenate([x[n:-n],seam])
 else:
  n=min(int(.004*sr),len(x)//8);x[:n]*=np.linspace(0,1,n)
  n=min(int(.025*sr),len(x)//8);x[-n:]*=np.linspace(1,0,n)
 gain=peak/max(float(np.max(abs(x))),1e-9);x*=gain
 sf.write(out/(name+'.wav'),x,sr,subtype='PCM_16')
 report[name]={'source_id':ident,'source_url':sources[ident]['page'],'excerpt_seconds':[start,end],
  'seconds':len(x)/sr,'peak':float(np.max(abs(x))),'rms':float(np.sqrt(np.mean(x*x))),
  'gain_db':20*math.log10(gain),'highpass_hz':cut,'loop':loop,
  'edits':'Excerpt, mono/48kHz, high-pass, DC removal, constant gain, fades or circular seam crossfade; original pitch.'}
 clips.extend([x,np.zeros(int(.6*sr))])
sf.write(out/'Audition.wav',np.concatenate(clips),sr,subtype='PCM_16')
(base/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
