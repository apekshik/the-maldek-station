"""Recorded sources only: trim, filter, circular crossfade and gain; spatial mono PCM."""
from pathlib import Path
import json,hashlib,math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly,butter,sosfiltfilt
p=Path(__file__).resolve().parent;out=p/'wav';out.mkdir(exist_ok=True)
sources=json.loads((p/'downloads.json').read_text());report=[]
def read(name,start,end):
 x,sr=sf.read(p/'originals'/(name+'.mp3'),always_2d=True);x=x[int(start*sr):int(end*sr)].mean(axis=1);g=math.gcd(sr,48000);x=resample_poly(x,48000//g,sr//g);x-=x.mean();return x
def loop(x):
 n=12000;w=np.linspace(0,1,n);return np.concatenate([x[n:-n],x[-n:]*(1-w)+x[:n]*w])
def save(name,x,rms,looping,source,excerpt):
 if looping:
  # Tame recorded transient peaks so the machinery can be prominent without hard clipping.
  x=np.tanh(x/max(2*np.sqrt(np.mean(x*x)),1e-8))
 x*=min(rms/max(1e-8,np.sqrt(np.mean(x*x))),(.34 if looping else .60)/max(1e-8,np.max(np.abs(x))))
 if not looping:
  n=min(960,len(x)//8);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
 sf.write(out/(name+'.wav'),x,48000,subtype='PCM_16');report.append({'asset':name,'loop':looping,'source':source,'excerpt_seconds':excerpt,'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x)))),'peak_dbfs':float(20*np.log10(np.max(np.abs(x)))),'duration':len(x)/48000})
motor=sosfiltfilt(butter(3,[65,5500],btype='bandpass',fs=48000,output='sos'),read('ElectricMotor',2,18))
save('Motor_Load_Loop',loop(motor),.20,True,'ElectricMotor',[2,18])
hum=sosfiltfilt(butter(3,[45,2200],btype='bandpass',fs=48000,output='sos'),read('MotorHum',8,28))
save('Gearbox_Loop',loop(hum),.15,True,'MotorHum',[8,28])
wheel=sosfiltfilt(butter(3,[180,6500],btype='bandpass',fs=48000,output='sos'),read('WheelMechanism',12,27))
save('Bullwheel_Roll_Loop',loop(wheel),.13,True,'WheelMechanism',[12,27])
roller=sosfiltfilt(butter(3,[350,4200],btype='bandpass',fs=48000,output='sos'),read('WheelMechanism',16,24))
save('Pylon_Roller_Loop',loop(roller),.10,True,'WheelMechanism',[16,24])
# Use the strongest short mechanical transient in the terminal recording for brake engagement.
x=read('WheelMechanism',12,27);window=4800;power=np.convolve(x*x,np.ones(window)/window,mode='valid')[::480];i=int(np.argmax(power))*480;i=max(0,min(i-2400,len(x)-48000))
save('Brake_Set',x[i:i+48000].copy(),.12,False,'WheelMechanism',[12+i/48000,13+i/48000])
save('Brake_Release',x[i:i+24000].copy(),.10,False,'WheelMechanism',[12+i/48000,12.5+i/48000])
for row in sources:
 row['sha256']=hashlib.sha256((p/'originals'/(row['name']+'.mp3')).read_bytes()).hexdigest();row['license_url']='https://creativecommons.org/licenses/by/4.0/' if row['license']=='CC-BY-4.0' else 'https://creativecommons.org/publicdomain/zero/1.0/'
(p/'sources.json').write_text(json.dumps({'sources':sources,'assets':report,'edits':'Mono 48 kHz, DC removal, band filtering, soft peak compression, gain, 250ms circular loop crossfades; one-shot trims/fades. No generated audio.'},indent=2));print(json.dumps(report,indent=2))
