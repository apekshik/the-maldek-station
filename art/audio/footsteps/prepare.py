from pathlib import Path
import numpy as np,soundfile as sf,json
root=Path(__file__).resolve().parent;out=root/'wav';out.mkdir(exist_ok=True)
def read(p):
 x,sr=sf.read(p);x=x.mean(axis=1) if x.ndim>1 else x
 # Resample to a consistent 48kHz for mixing and import.
 x=np.interp(np.arange(round(len(x)*48000/sr))*sr/48000,np.arange(len(x)),x)
 return x
sources={}
for kind,pattern in [('soil','footstep_grass_*'),('concrete','footstep_concrete_*'),('wood','footstep_wood_*')]:
 for i,p in enumerate(sorted((root/'kenney/Audio').glob(pattern))):
  x=read(p);x=x/(max(abs(x).max(),.001))*0.55;name=f'Step_{kind}_{i:02}';sf.write(out/(name+'.wav'),x,48000,subtype='PCM_16');sources[name]=str(p.relative_to(root))
# Gravel uses the recorded crunch combined with varied shoe impacts.
gravel=read(root/'tinyworlds/gravel.ogg')
for i,p in enumerate(sorted((root/'kenney/Audio').glob('footstep_concrete_*'))):
 shoe=read(p);n=max(len(shoe),len(gravel));x=np.zeros(n);x[:len(shoe)]+=.45*shoe;x[:len(gravel)]+=.8*gravel;x=x/max(abs(x).max(),.001)*.6;name=f'Step_gravel_{i:02}';sf.write(out/(name+'.wav'),x,48000,subtype='PCM_16');sources[name]=['tinyworlds/gravel.ogg',str(p.relative_to(root))]
# A restrained metal resonance sits under the shoe transient.
for i,p in enumerate(sorted((root/'kenney/Audio').glob('impactMetal_light_*'))):
 ring=read(p);shoe=read(root/f'kenney/Audio/footstep_concrete_{i:03}.ogg');n=max(len(shoe),len(ring));x=np.zeros(n);x[:len(shoe)]+=.8*shoe;x[:len(ring)]+=.25*ring;x=x/max(abs(x).max(),.001)*.6;name=f'Step_metal_{i:02}';sf.write(out/(name+'.wav'),x,48000,subtype='PCM_16');sources[name]=[str(p.relative_to(root)),f'kenney/Audio/footstep_concrete_{i:03}.ogg']
(root/'sources.json').write_text(json.dumps(sources,indent=2))
print(f'Prepared {len(sources)} mono 48kHz footsteps')
