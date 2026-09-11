from pathlib import Path
import soundfile as sf,numpy as np,json,hashlib,math
from scipy.signal import butter,sosfiltfilt,resample_poly
b=Path(__file__).resolve().parent;(b/'wav').mkdir(exist_ok=True);SR=48000;records={};report=[]
def load(name):
 if name not in records:
  f=b/'originals'/(name+'.mp3');x,s=sf.read(f,always_2d=True);x=x.mean(1);g=math.gcd(s,SR);records[name]=resample_poly(x,SR//g,s//g)
 return records[name]
def make(name,source,start,end,lp=3000,peak=.6,bass=0,loop=False):
 x=load(source)[round(start*SR):round(end*SR)].copy();assert len(x)>1000
 x-=x.mean();x=sosfiltfilt(butter(2,35,fs=SR,btype='highpass',output='sos'),x);x=sosfiltfilt(butter(3,lp,fs=SR,output='sos'),x)
 if bass:x+=bass*sosfiltfilt(butter(2,230,fs=SR,output='sos'),x)
 if loop:
  n=SR*3;t=np.linspace(0,1,n);x=np.concatenate([x[n:-n],x[-n:]*(1-t)+x[:n]*t])
 else:
  n=min(240,len(x)//10);x[:n]*=np.linspace(0,1,n);n=min(1200,len(x)//10);x[-n:]*=np.linspace(1,0,n)
 gain=peak/max(abs(x));x*=gain;f=b/'wav'/(name+'.wav');sf.write(f,x,SR,subtype='PCM_16')
 report.append({'asset':name,'source':source,'excerpt':[start,end],'lowpass_hz':lp,'bass_layer_gain':bass,'peak':float(max(abs(x))),'rms':float(np.sqrt(np.mean(x*x))),'gain_db':float(20*np.log10(gain)),'seconds':len(x)/SR,'loop':loop,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
for kind,source,starts in [('LockerOpen','locker',[.3,8.15,17.1]),('LockerClose','locker',[4.55,12.8,21.4]),('DrawerOpen','drawer',[2.65,5.95,11.65]),('DrawerClose','drawer',[4.15,6.95,9.8]),('CupboardOpen','cupboard',[.2,3.55]),('CupboardClose','cupboard',[1.8,4.8]),('FridgeOpen','fridge',[.15]),('FridgeClose','fridge',[5.6,13.65]),('RoomOpen','room',[4.85,17.45,22.6]),('RoomClose','room',[9.85,14.55,30.95])]:
 for i,t in enumerate(starts):make(f'{kind}_{i:02}',source,t,t+.85,lp=2400 if kind.startswith('Room') else 3200,peak=.6,bass=.4)
make('FridgeOpen_01','fridge_alt',6.2,7.05,lp=2200,peak=.6,bass=.4)
for i,t in enumerate([9.2,30.2]):make(f'RoomTravelClose_{i:02}','room',t,t+.55,lp=1800,peak=.15,bass=.3)
for kind,starts in [('Tile',[.82,1.74,2.66,3.57,4.48,5.42]),('Concrete',[.20,1.13,2.46,3.18,5.86,8.28])]:
 for i,t in enumerate(starts):make(f'Step{kind}_{i:02}',kind.lower(),t,t+.54,lp=1550 if kind=='Tile' else 1250,peak=.62,bass=1.2)
make('ShelteredStorm','wind',15,105,lp=850,peak=.72,bass=.7,loop=True)
# Keep source metal-door creak as alternate recorded takes for full-size exterior doors.
for source,id in [('steel_open',700682),('steel_close',700705)]:
 f=b.parent/'doors/recorded/originals'/f'{id}.mp3';x,s=sf.read(f,always_2d=True);g=math.gcd(s,SR);records[source]=resample_poly(x.mean(1),SR//g,s//g)
 for i,t in enumerate([.12,.86]):make(('SteelOpen' if source=='steel_open' else 'SteelClose')+f'_{i:02}',source,t,t+.74,lp=2300,peak=.42,bass=.35,loop=False)
(b/'edits.json').write_text(json.dumps(report,indent=2))
for group in ['StepTile','StepConcrete','Locker','Drawer','Cupboard','Fridge','Room','Steel']:
 clips=[]
 for r in report:
  if r['asset'].startswith(group):x,_=sf.read(b/'wav'/(r['asset']+'.wav'));clips.extend([x,np.zeros(int(.35*SR))])
 sf.write(b/(group+'_audition.wav'),np.concatenate(clips),SR,subtype='PCM_16')
print(len(report),'recorded excerpts prepared')
