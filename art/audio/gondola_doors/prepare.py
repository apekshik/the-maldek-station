"""Edit downloaded real door recordings for the cabin study. No generated audio."""
from pathlib import Path
import json,hashlib,math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
b=Path(__file__).resolve().parent;(b/'wav').mkdir(exist_ok=True)
rows=[]
for ident,name,title,author,url,peak in [
 (439499,'Gondola_Door_Open','Train Door Opening','iamaviolin','https://freesound.org/people/iamaviolin/sounds/439499/',.60),
 (439494,'Gondola_Door_Close','Train Door Closing','iamaviolin','https://freesound.org/people/iamaviolin/sounds/439494/',.60),
 (509114,'Metal_Track_Alternate','Door sliding along a metal track','wlabarron','https://freesound.org/people/wlabarron/sounds/509114/',.55)]:
 p=b/'originals'/f'{ident}.mp3';x,sr=sf.read(p,always_2d=True);x=x.mean(axis=1);g=math.gcd(sr,48000);x=resample_poly(x,48000//g,sr//g);x-=x.mean();n=192;x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n);gain=peak/max(abs(x));x*=gain
 target=b/'wav'/f'{name}.wav';sf.write(target,x,48000,subtype='PCM_16')
 rows.append({'asset':name,'title':title,'author':author,'page':url,'license':'CC0-1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','download':'https://cdn.freesound.org/previews/'+str(ident//1000)+'/'+str(ident)+('_6470379-hq.mp3' if ident in [439499,439494] else '_3782735-hq.mp3'),'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'wav_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'seconds':len(x)/48000,'peak':float(max(abs(x))),'rms':float(np.sqrt(np.mean(x*x))),'gain_db':20*math.log10(gain),'edits':'Complete recording; mono 48kHz PCM16, DC removal, constant gain, 4ms edge fades. No synthesis, layering or pitch changes.','role':'alternate audition' if ident==509114 else 'opening' if ident==439499 else 'closing'})
(b/'sources.json').write_text(json.dumps(rows,indent=2)+'\n')
# Sequence timing follows the Blender review, with silence for the boarding dwell.
mix=np.zeros(384*2000+48000)
for name,frame in [('Gondola_Door_Open',78),('Gondola_Door_Close',264)]:
 x,_=sf.read(b/'wav'/f'{name}.wav');start=(frame-1)*2000;mix[start:start+len(x)]+=x
sf.write(b/'wav'/'Cabin_Door_Sequence_Audition.wav',mix,48000,subtype='PCM_16')
print(json.dumps(rows,indent=2))
