"""Recorded CC0 chimes and air brakes: trims, EQ, gentle peak compression, gain and fades only."""
from pathlib import Path
import json,math
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfiltfilt,resample_poly
p=Path(__file__).resolve().parent;(p/'wav').mkdir(exist_ok=True);rows=[]
def read(name,a,b,low,high):
 x,s=sf.read(p/'originals'/(name+'.mp3'),always_2d=True);x=x[int(a*s):int(b*s)].mean(axis=1);g=math.gcd(s,48000);x=resample_poly(x,48000//g,s//g);x-=x.mean()
 return sosfiltfilt(butter(2,[low,high],fs=48000,btype='bandpass',output='sos'),x)
def save(name,x,source,excerpt,rms=.19):
 x=np.tanh(x/max(3*np.sqrt(np.mean(x*x)),1e-9))
 x*=min(rms/max(np.sqrt(np.mean(x*x)),1e-9),.56/max(abs(x).max(),1e-9));n=min(480,len(x)//8);x[:n]*=np.linspace(0,1,n);n=min(4800,len(x)//5);x[-n:]*=np.linspace(1,0,n)
 sf.write(p/'wav'/(name+'.wav'),x,48000,subtype='PCM_16');rows.append(dict(asset=name,source=source,excerpt=excerpt,duration=len(x)/48000,peak=float(abs(x).max()),rms=float(np.sqrt(np.mean(x*x)))))
save('Platform_Arriving',read('DoorChime',0,1.48,180,6000),'DoorChime',[0,1.48])
save('Platform_Board',read('ElevatorChime',.27,1.95,220,6500),'ElevatorChime',[.27,1.95])
x=read('DoorChime',1.5,2.6,180,6000);save('Platform_Depart',np.concatenate([x,np.zeros(9600),x]),'DoorChime',[1.5,2.6,'repeated with 200ms gap'])
save('Platform_Away',read('DoorChime',1.5,2.3,220,4500),'DoorChime',[1.5,2.3],.10)
save('Gondola_Dock_Whoosh',read('AirBrakes',0,1.65,300,9500),'AirBrakes',[0,1.65],.20)
(p/'verification.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
credits='GONDOLA PLATFORM AND ARRIVAL AUDIO\nAll sources CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/\n\n'
for s in json.loads((p/'sources.json').read_text()):credits+=s['name']+' by '+s['author']+'\n'+s['source']+'\n\n'
credits+='Edits: mono 48kHz PCM, trims, bandpass EQ, gentle peak compression, gain, edge fades; departure repeats a recorded bell. No synthesized audio. Freesound high-quality MP3 previews retained as source files.\n'
(p/'CREDITS.txt').write_text(credits);(p.parents[2]/'game/Content/AudioCredits/GondolaArrival.txt').write_text(credits)
