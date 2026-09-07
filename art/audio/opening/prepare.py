"""Source edits only: recorded switch clicks and a licensed Nox atmosphere excerpt."""
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
 x*=.35/max(abs(x));n=min(96,len(x)//2);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
 sf.write(p/'wav'/f'{name}.wav',x,rate,subtype='PCM_16')
 rows.append({'asset':name,'author':'Rudmer_Rotteveel','source':f'https://freesound.org/people/Rudmer_Rotteveel/sounds/{457458 if i==1 else 457463}/','license':'CC0-1.0','download':'Public high-quality MP3 preview','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'seconds':len(x)/rate})
z=zipfile.ZipFile(p.parent/'recorded_foley/Nox_Essentials.zip');name='Essentials_Series_NOX_SOUND/Nature_Essentials_NOX_SOUND/Ambiance_Cave_Dark_Loop_Stereo.wav';raw=z.read(name);(p/'originals'/'Nox_Cave_Dark.wav').write_bytes(raw)
x,s=sf.read(io.BytesIO(raw),always_2d=True);x=x[:int(s*14)]
x=resample_poly(x,rate//gcd(s,rate),s//gcd(s,rate),axis=0)
x*=min(.055/np.sqrt(np.mean(x*x)),.3/np.max(abs(x)))
t=np.arange(len(x))/rate;envelope=np.minimum(np.clip(t/2.5,0,1),np.clip((14-t)/5,0,1));envelope=envelope*envelope*(3-2*envelope);x*=envelope[:,None]
sf.write(p/'wav'/'Opening_Atmosphere.wav',x,rate,subtype='PCM_16')
rows.append({'asset':'Opening_Atmosphere','author':'Nox_Sound_Design','source':'https://nox-sound-design.itch.io/essentials-series-sfx-nox-sound','license':'CC0-1.0','original':name,'sha256':hashlib.sha256(raw).hexdigest(),'excerpt_seconds':[0,14],'edits':'Gain, 2.5-second fade-in, 5-second fade-out. No synthesized or generated audio.'})
(p/'sources.json').write_text(json.dumps(rows,indent=2));print(rows)
