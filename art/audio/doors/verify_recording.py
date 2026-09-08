import wave,numpy as np,json
from pathlib import Path
root=Path('C:/Users/apek-anna/Developer/the-maldek-station');p=root/'art/unreal_handoff/revision12/doors/audio_review/door_and_keypad_mix.wav'
with wave.open(str(p),'rb') as f:
 assert f.getsampwidth()==2
 x=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)/32768;sr=f.getframerate();channels=f.getnchannels()
r={'seconds':len(x)/sr/channels,'sample_rate':sr,'channels':channels,'peak':float(abs(x).max()),'rms':float(np.sqrt(np.mean(x*x))),'nonzero_samples':int(np.count_nonzero(x))};print(r);assert r['rms']>.0001 and r['peak']<.999;r['success']=True;(p.parent/'recording_analysis.json').write_text(json.dumps(r,indent=2));print(r)
