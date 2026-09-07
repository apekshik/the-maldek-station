"""Prepare sourced recordings as spatial mono loops. No synthesis."""
from pathlib import Path
from math import gcd
import hashlib,json
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
p=Path(__file__).resolve().parent;(p/'wav').mkdir(exist_ok=True)
rows=[]
for name,author,source,start,end,rms in [
 ('Generator','qubodup','https://freesound.org/people/qubodup/sounds/189896/',2,42,.15),
 ('Flywheel','Nox_Sound','https://freesound.org/people/Nox_Sound/sounds/559470/',0,9.49,.09),
 ('Ventilation','iccleste','https://freesound.org/people/iccleste/sounds/260815/',3,53,.08),
 ('Cable','mikewest','https://freesound.org/people/mikewest/sounds/394222/',1,21,.12)]:
 f=p/'originals'/f'{name}.mp3';x,rate=sf.read(f,always_2d=True)
 x=x[int(start*rate):int(end*rate)].mean(axis=1)
 x=resample_poly(x,48000//gcd(rate,48000),rate//gcd(rate,48000));x-=x.mean()
 n=12000;w=np.linspace(0,1,n)
 x=np.concatenate([x[n:-n],x[-n:]*(1-w)+x[:n]*w])
 x*=min(rms/np.sqrt(np.mean(x*x)),.7/np.max(np.abs(x)))
 sf.write(p/'wav'/f'{name}_Loop.wav',x,48000,subtype='PCM_16')
 rows.append(dict(asset=f'{name}_Loop',author=author,source=source,license='CC0-1.0',license_url='https://creativecommons.org/publicdomain/zero/1.0/',download='Public high-quality MP3 preview',sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_excerpt=[start,end],seconds=len(x)/48000,peak=float(np.max(np.abs(x))),rms=float(np.sqrt(np.mean(x*x))),edits='Mono, 48kHz, DC removal, constant gain, 250ms circular seam crossfade. Original pitch retained.'))
(p/'sources.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
