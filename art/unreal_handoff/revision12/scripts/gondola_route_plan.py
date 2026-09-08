"""Offline, metre-based route profile. Illustrative cable equilibrium, not certification."""
import json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route'
s=json.loads((out/'survey.json').read_text());rows=s['samples'];offset=5.927
indices=[0,67,119,172,222,260,280]
nodes=[]
for j,i in enumerate(indices):
 r=rows[i];x,y=[v/100 for v in r['xy']];g=max(r[k][2]/100 for k in ['centre','left','right'])
 z=s['start'][2]/100+offset if j==0 else (r['centre'][2]/100+5+offset if j==6 else g+42.327)
 nodes.append({'x':x,'y':y,'z':z,'ground':g,'index':i})
w=12*9.81;H=250000
# Every tower carries downward rope reaction, including the shallow approach to
# its roller bank. Raise nodes that would otherwise need an upper hold-down bank.
for iteration in range(2000):
 change=0
 for i in range(1,6):
  a,c,d=nodes[i-1:i+2];l=c['y']-a['y'];r=d['y']-c['y']
  minimum=(d['z']/r+a['z']/l-w*(l+r)/(2*H)+.025)/(1/l+1/r)
  delta=max(0,minimum-c['z']);c['z']+=delta;change=max(change,delta)
 if change<1e-7:break
def height(y):
 k=next((i for i in range(6) if y<=nodes[i+1]['y']),5)
 a,c=nodes[k:k+2];L=c['y']-a['y'];d=y-a['y'];z=a['z']+(c['z']-a['z'])*d/L-w*d*(L-d)/(2*H)
 for i,n in enumerate(nodes[1:-1],1):
  q=y-n['y'];edge=4.2
  if abs(q)<edge:
   left=nodes[i-1];right=nodes[i+1];ll=n['y']-left['y'];rr=right['y']-n['y']
   si=(n['z']-left['z'])/ll+w*ll/(2*H);so=(right['z']-n['z'])/rr-w*rr/(2*H)
   z=n['z']+(si+so)*q/2-(si-so)*(q*q/(4*edge)+edge/4)+w*q*q/(2*H)
 return z,k
samples=[];length=0;prev=None
for i in range(1386):
 y=nodes[0]['y']+(nodes[-1]['y']-nodes[0]['y'])*i/1385;z,k=height(y);x=nodes[0]['x']+(nodes[-1]['x']-nodes[0]['x'])*i/1385
 if prev:length+=math.dist(prev,[x,y,z])
 samples.append([x,y,z]);prev=[x,y,z]
clear=[]
for row in rows:
 y=row['xy'][1]/100;z,k=height(y);a,c=nodes[k:k+2];L=c['y']-a['y'];d=y-a['y']
 # Additional conservative stationary point-load sag (1800 kg) at the carrier.
 live=1800*9.81*d*(L-d)/(H*L)
 clear.append({'metres':y-nodes[0]['y'],'floor_clearance_m':z-offset-row['centre'][2]/100,'loaded_clearance_m':z-offset-live-row['centre'][2]/100})
for i,n in enumerate(nodes[1:-1],1):
 a,c=nodes[i-1],nodes[i+1];l=n['y']-a['y'];r=c['y']-n['y']
 incoming=(n['z']-a['z'])/l+w*l/(2*H);outgoing=(c['z']-n['z'])/r-w*r/(2*H)
 n.update(contact_z=height(n['y'])[0],height=height(n['y'])[0]-n['ground'],grade=(incoming+outgoing)/2,reaction_per_rope_N=H*(incoming-outgoing))
result={'nodes':nodes,'rope_samples_m':samples,'rope_offset_m':offset,'length_m':length,'clearance':clear,'assumptions':{'rope_kg_m':12,'horizontal_tension_N':H,'loaded_cabin_kg':1800,'minimum_tower_downward_reaction_N':6250},'limitations':'Static parabolic cable envelope; fixed visual sag. No rope strength, dynamic sag or foundation capacity certification.'}
(out/'plan.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'length_m':length,'towers':nodes[1:-1],'min_loaded_clearance_outside_terminals_m':min(r['loaded_clearance_m'] for r in clear if 15<r['metres']<length-25)},indent=2))
