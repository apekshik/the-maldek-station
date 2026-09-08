"""Original designed keypad/steel-door effects, 48 kHz mono PCM; deterministic synthesis."""
from pathlib import Path
import numpy as np,wave,json
out=Path(__file__).resolve().parent/'wav';out.mkdir(parents=True,exist_ok=True);sr=48000;rng=np.random.default_rng(3907);report={}
def tone(freq,dur,gain=.15):
 t=np.arange(int(sr*dur))/sr;e=np.minimum(t/.003,1)*np.exp(-t/(dur*.28));return gain*np.sin(2*np.pi*freq*t)*e
def click(dur=.1):
 t=np.arange(int(sr*dur))/sr;n=rng.normal(size=len(t));n=np.convolve(n,np.ones(3)/3,'same');return .14*n*np.exp(-t/ .008)+tone(2400,dur,.065)
def mix(parts,dur):
 a=np.zeros(int(sr*dur))
 for time,x in parts:
  i=int(sr*time);n=min(len(x),len(a)-i);a[i:i+n]+=x[:n]
 return a
def save(name,x):
 x=x-np.mean(x);x=np.tanh(x);x[:120]*=np.linspace(0,1,120);x[-240:]*=np.linspace(1,0,240)
 assert np.max(np.abs(x))<.95
 with wave.open(str(out/(name+'.wav')),'wb') as f:f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes((x*32767).astype('<i2').tobytes())
 report[name]={'seconds':len(x)/sr,'peak':float(np.max(np.abs(x))),'rms':float(np.sqrt(np.mean(x*x)))}
save('KeyPress',mix([(0,click()),(.016,tone(1350,.085,.14))],.14))
save('KeyClear',mix([(0,click()),(.018,tone(1100,.08)),(.095,tone(740,.11))],.24))
save('KeyConfirm',mix([(0,click()),(.015,tone(1050,.10)),(.105,tone(1580,.16))],.32))
save('KeyReject',mix([(0,click()),(.018,tone(250,.12,.19)),(.16,tone(230,.16,.17))],.38))
def metal(dur,weight):
 t=np.arange(int(sr*dur))/sr;a=np.zeros(len(t))
 for f,g,decay in [(92,.28,.09),(178,.19,.06),(420,.1,.10),(930,.07,.075),(1743,.045,.05)]:a+=g*np.sin(2*np.pi*f*t+rng.random()*2)*np.exp(-t/decay)
 a+=rng.normal(size=len(t))*.14*np.exp(-t/.015);return a*weight
save('DoorUnlatch',mix([(0,metal(.20,.55)),(.065,click(.12)),(.115,metal(.23,.3))],.4))
save('DoorClose',mix([(0,metal(.48,1.05)),(.055,metal(.3,.32)),(.13,click(.12))],.65))
# Quiet rounded friction and modulated metallic hinge resonances; smooth periodic seam.
t=np.arange(sr)/sr;n=rng.normal(size=sr);n=np.convolve(n,np.ones(40)/40,'same')
a=.16*n+.045*np.sin(2*np.pi*143*t+1.2*np.sin(2*np.pi*3*t))+.022*np.sin(2*np.pi*317*t+.5*np.sin(2*np.pi*5*t));a*=.65+.35*np.sin(2*np.pi*t)**2
save('DoorMovement',a)
(out.parent/'manifest.json').write_text(json.dumps({'provenance':'Original deterministic synthesized sound design, not field recordings. No external samples.','sample_rate':sr,'assets':report},indent=2))
# Audition: key, clear, accept, reject, unlatch, movement, close.
parts=[];cursor=0
for name in report:
 with wave.open(str(out/(name+'.wav')),'rb') as f:x=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)/32768
 parts.append((cursor,x));cursor+=len(x)/sr+.35
save('Audition',mix(parts,cursor))
