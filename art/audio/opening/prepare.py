"""Recorded switch clicks and the user's selected A/B licensed atmospheres."""
from pathlib import Path
import zipfile,io,json,hashlib
import soundfile as sf
import numpy as np
from scipy.signal import resample_poly
from math import gcd
p=Path(__file__).resolve().parent;rate=48000;rows=[]
for i,name in [(1,'Flashlight_On'),(2,'Flashlight_Off')]:
 f=p/'originals'/f'Flashlight_Click_{i:02}.mp3';x,s=sf.read(f,always_2d=True);x=x.mean(axis=1)
 x=resample_poly(x,rate//gcd(s,rate),s//gcd(s,rate))
 nz=np.flatnonzero(abs(x)>max(abs(x))*.01);x=x[max(0,nz[0]-144):min(len(x),nz[-1]+480)]
 x*=.85/max(abs(x));n=min(96,len(x)//2);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
 sf.write(p/'wav'/f'{name}.wav',x,rate,subtype='PCM_16')
 rows.append({'asset':name,'author':'Rudmer_Rotteveel','source':f'https://freesound.org/people/Rudmer_Rotteveel/sounds/{457458 if i==1 else 457463}/','license':'CC0-1.0','download':'Public high-quality MP3 preview','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'seconds':len(x)/rate})
originals=p.parent/'auditions/2026-09-07/originals'
for asset,name,author,source,license_id in [
 ('Opening_Atmosphere','A_dark_cavern_ambient_001.ogg','Paul Wortmann','https://opengameart.org/content/dark-cavern-ambient','CC0-1.0'),
 ('Station_Atmosphere','B_dark_ambient_drone_2_loop.flac','Tsorthan Grove','https://opengameart.org/content/dark-ambient-drone-2','CC-BY-4.0')]:
 f=originals/name;x,s=sf.read(f,always_2d=True)
 if asset=='Opening_Atmosphere':x=x[:int(s*35)]
 x=resample_poly(x,rate//gcd(s,rate),s//gcd(s,rate),axis=0)
 x*=min(.085/np.sqrt(np.mean(x*x)),.6/np.max(abs(x)))
 if asset=='Opening_Atmosphere':
  t=np.arange(len(x))/rate;envelope=np.minimum(np.clip(t/2,0,1),np.clip((35-t)/8,0,1));envelope=envelope*envelope*(3-2*envelope);x*=envelope[:,None]
 sf.write(p/'wav'/f'{asset}.wav',x,rate,subtype='PCM_16')
 rows.append({'asset':asset,'author':author,'source':source,'license':license_id,'original':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'seconds':len(x)/rate,'edits':'Constant gain and resampling. Opening: first 35 seconds, 2-second fade-in, 8-second fade-out. Station: creator-provided loop, runtime 5-second fade-in. No generated audio.'})
(p/'sources.json').write_text(json.dumps(rows,indent=2));print(rows)
