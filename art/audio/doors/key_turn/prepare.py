"""Prepare a real recorded key turn. No synthesis, layers or pitch changes."""
from pathlib import Path
import hashlib,json,math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
b=Path(__file__).resolve().parent
p=b/'originals/418846.mp3'
x,sr=sf.read(p);x=x.mean(axis=1) if x.ndim==2 else x
if sr!=48000:
 g=math.gcd(sr,48000);x=resample_poly(x,48000//g,sr//g)
x-=x.mean()
n=192;x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
x*=.48/max(abs(x))
sf.write(b/'KeyTurn.wav',x,48000,subtype='PCM_16')
report={'title':'Key Twist in lock','author':'KieranKeegan','source_url':'https://freesound.org/people/KieranKeegan/sounds/418846/',
 'download_url':'https://cdn.freesound.org/previews/418/418846_6616210-hq.mp3','license':'CC0-1.0',
 'license_url':'https://creativecommons.org/publicdomain/zero/1.0/','retrieved':'2026-09-08',
 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((b/'KeyTurn.wav').read_bytes()).hexdigest(),
 'seconds':len(x)/48000,'peak':float(max(abs(x))),'rms':float(np.sqrt(np.mean(x*x))),
 'edits':'Full recording, mono 48kHz PCM16, DC removal, constant gain, 4ms edge fades. Original pitch. No generated audio.'}
(b/'source.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
