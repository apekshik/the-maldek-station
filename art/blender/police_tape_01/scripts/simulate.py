"""Deterministic metre-scale ribbon centreline study; no Blender dependency.

Position-based dynamics at 120 Hz. Two flexible chains share a releasable seam.
This is a design preview, not Unreal runtime physics or a material fracture model.
"""
import json, math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
WIDTH = .0762
N = 64
SEAM = 36
ANCHORS = [(-1.59, 0., 1.28), (1.59, 0., 1.38)]

def run(retreat=False):
    positions = []
    for i in list(range(SEAM+1)) + list(range(SEAM, N+1)):
        u = i/N
        positions.append([ANCHORS[0][k]+(ANCHORS[1][k]-ANCHORS[0][k])*u-(.11*math.sin(math.pi*u) if k==2 else 0) for k in range(3)])
    old = [p[:] for p in positions]
    split = SEAM+1
    links = [(i, i+1, math.dist(positions[i],positions[i+1])*1.002) for i in range(len(positions)-1) if i != SEAM]
    broken = False
    break_frame = None
    frames = []
    max_error = 0.
    dt = 1/120
    for step in range(144*5):
        t = step*dt
        if retreat:
            py = -1.2 + .98 * max(0., 1-abs(t-2.2)/1.0)
        else:
            py = -1.2 + 2.7 * max(0., min(1., (t-1.2)/2.6))
        for i,p in enumerate(positions):
            if i in (0,len(positions)-1): continue
            velocity = [(p[k]-old[i][k])*.988 for k in range(3)]
            old[i] = p[:]
            wind = .65*math.sin(t*2.1+i*.18)+.30*math.sin(t*4.7)
            p[0] += velocity[0]
            p[1] += velocity[1]+wind*dt*dt
            p[2] += velocity[2]-9.81*dt*dt
        for iteration in range(32):
            for a,b,rest in links + ([] if broken else [(SEAM,split,0.)]):
                pa,pb = positions[a],positions[b]
                d = [pb[k]-pa[k] for k in range(3)]
                length = math.sqrt(sum(v*v for v in d))
                if length < 1e-10: continue
                wa = 0 if a==0 else 1
                wb = 0 if b==len(positions)-1 else 1
                correction = (length-rest)/(length*(wa+wb))
                for k in range(3):
                    pa[k] += d[k]*correction*wa
                    pb[k] -= d[k]*correction*wb
            for i,p in enumerate(positions):
                if i in (0,len(positions)-1): continue
                dx,dy = p[0]-.12,p[1]-py
                radius = math.hypot(dx,dy)
                # Torso proxy. Contact is disabled only after the player has passed.
                if radius < .31 and .55 < p[2] < 1.72:
                    p[0] = .12+dx/max(radius,1e-8)*.31
                    p[1] = py+dy/max(radius,1e-8)*.31
                for tx in (-1.8,1.8):
                    dx,dy=p[0]-tx,p[1]
                    radius=math.hypot(dx,dy)
                    if radius < .23:
                        p[0]=tx+dx/max(radius,1e-8)*.23
                        p[1]=dy/max(radius,1e-8)*.23
                p[2] = max(.05,p[2])
            positions[0] = list(ANCHORS[0]); positions[-1] = list(ANCHORS[1])
        if not broken and positions[SEAM][1] > ANCHORS[0][1]+.36:
            broken = True
            break_frame = step//5+1
        if step%5 == 4:
            frames.append({'points':[p[:] for p in positions], 'player_y':py, 'broken':broken})
            max_error=max(max_error,max(abs(math.dist(positions[a],positions[b])-r) for a,b,r in links))
    assert all(math.isfinite(v) for f in frames for p in f['points'] for v in p)
    assert all(math.dist(f['points'][0],ANCHORS[0])<1e-8 and math.dist(f['points'][-1],ANCHORS[1])<1e-8 for f in frames)
    assert (break_frame is None) if retreat else (break_frame is not None)
    return {'fps':24,'width_m':WIDTH,'anchors_m':ANCHORS,'seam_indices':[SEAM,split], 'break_frame':break_frame,'max_segment_error_m':max_error,'frames':frames}

if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    data=run(); retreat=run(True)
    (OUT/'motion.json').write_text(json.dumps(data,separators=(',',':')))
    report={'forward_break_frame':data['break_frame'],'retreat_break_frame':retreat['break_frame'],'anchors_fixed':True,'finite_positions':True,'max_segment_error_m':data['max_segment_error_m'],'frame_count':len(data['frames'])}
    (OUT/'simulation_check.json').write_text(json.dumps(report,indent=2))
    print(report)
