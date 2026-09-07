"""Edit licensed recordings only: trim, resample, gain, fades, and recorded fabric mix."""
from pathlib import Path
import io,json,zipfile,hashlib
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from math import gcd

ROOT=Path(__file__).resolve().parent
RATE=48000
for directory in ['originals','dry','cloth','wav']:(ROOT/directory).mkdir(exist_ok=True)
def decode(data):
    x,s=sf.read(io.BytesIO(data),always_2d=True);x=x.mean(axis=1)
    if s!=RATE:x=resample_poly(x,RATE//gcd(s,RATE),s//gcd(s,RATE))
    return x
def fade(x):
    x=x.copy();n=min(int(.008*RATE),len(x)//2)
    x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    return x
def trim(x):
    active=np.flatnonzero(np.abs(x)>max(np.max(np.abs(x))*.008,.0001))
    start=max(0,int(active[0]) - int(.008*RATE));end=min(len(x),int(active[-1])+int(.045*RATE))
    return fade(x[start:end]),[start/RATE,end/RATE]
cloth=decode((ROOT/'rustling.ogg').read_bytes())
cloth_ranges=[(1.08,1.72),(10.60,11.12),(13.55,14.3),(22.80,23.35),(18.48,19.18),(23.95,24.48)]
cloths=[]
for i,(a,b) in enumerate(cloth_ranges):
    x=fade(cloth[int(a*RATE):int(b*RATE)])
    x*=.035/max(np.max(np.abs(x)),1e-8)
    sf.write(ROOT/'cloth'/f'Clothing_{i:02}.wav',x,RATE,subtype='PCM_16');cloths.append(x)
z=zipfile.ZipFile(ROOT/'Nox_Essentials.zip');cz=zipfile.ZipFile(ROOT/'congusbongus_footsteps.zip')
def nox(kind,limit):
    return [(z,n) for n in sorted(z.namelist()) if '/Footsteps_Essentials_NOX_SOUND/' in n and f'/Footsteps_{kind}_Walk/' in n and n.endswith('.wav')][:limit]
groups={'soil':nox('Leaves',6)+nox('Grass',6)+nox('DirtyGround',6),'gravel':nox('Gravel',10),'metal':nox('Metal',15),'concrete':[(cz,f'footsteps/boots/{i}.ogg') for i in range(9)],'wood':nox('Wood',10)}
manifest={'sources':[{'author':'Nox_Sound_Design','url':'https://nox-sound-design.itch.io/essentials-series-sfx-nox-sound','license':'CC0-1.0','recording':'Footsteps Essentials, outdoor recordings'},{'author':'swuing; mastered by congusbongus','url':'https://opengameart.org/content/footsteps-on-different-surfaces','original_url':'https://freesound.org/people/swuing/sounds/38873/','license':'CC-BY-3.0','recording':'footstep-concrete.wav, boots subset'},{'author':'Iochi Glaucus','url':'https://opengameart.org/content/fabric-rustling','license':'CC0-1.0','recording':'AT2020 recording of fabric movement'}],'processing':'No synthesis or artificial impacts. Actual footstep recordings, silence trimming, mono 48kHz conversion, group gain, 8ms fades, quiet recorded fabric layer starting 80ms after foot contact. Dry and fabric stems retained.','cloth_ranges_seconds':cloth_ranges,'samples':[]}
preview=[]
for kind,files in groups.items():
    decoded=[]
    for archive,name in files:
        raw=archive.read(name);original=ROOT/'originals'/f'{kind}_{Path(name).name}';original.write_bytes(raw)
        x,span=trim(decode(raw));decoded.append((x,span,name,hashlib.sha256(raw).hexdigest()))
    # One gain per bank preserves natural differences between takes.
    median_rms=np.median([np.sqrt(np.mean(x*x)) for x,*_ in decoded])
    gain=min(.065/max(median_rms,1e-8),.68/max(np.max(np.abs(x)) for x,*_ in decoded))
    for i,(x,span,name,digest) in enumerate(decoded):
        x=x*gain;stem=f'Recorded_{kind}_{i:02}'
        sf.write(ROOT/'dry'/f'{stem}.wav',x,RATE,subtype='PCM_16')
        cloth_index=i%len(cloths);c=cloths[cloth_index];offset=int(.08*RATE)
        mixed=np.zeros(max(len(x),len(c)+offset));mixed[:len(x)]+=x;mixed[offset:offset+len(c)]+=c
        assert np.max(np.abs(mixed))<.85
        sf.write(ROOT/'wav'/f'{stem}.wav',mixed,RATE,subtype='PCM_16')
        manifest['samples'].append({'asset':stem,'surface':kind,'original':name,'sha256':digest,'trim_seconds':span,'gain':float(gain),'cloth_index':cloth_index,'duration':len(mixed)/RATE,'peak':float(np.max(np.abs(mixed)))})
        if i<4:preview.append(mixed);preview.append(np.zeros(int(.15*RATE)))
    preview.append(np.zeros(RATE))
sf.write(ROOT/'recorded_foley_preview.wav',np.concatenate(preview),RATE,subtype='PCM_16')
(ROOT/'sources.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'concrete_source_license.txt').write_bytes(cz.read('footsteps/boots/license.txt'))
print(json.dumps({'counts':{k:len(v) for k,v in groups.items()},'max_peak':max(s['peak'] for s in manifest['samples'])}))
