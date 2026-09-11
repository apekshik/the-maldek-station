"""Coupled crisscross study. Thin, anisotropic contact proxies, not full cloth."""
import numpy as np,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
ANCHORS=np.array([[[-1.59,-.008,.97],[1.59,-.008,1.72]],[[-1.59,.008,1.71],[1.59,.008,.98]],[[-1.59,0,1.24],[1.59,0,1.40]]])
N=64;SEAM=36
def run(mode='forward',contact=True):
    u=np.array(list(range(37))+list(range(36,65)))/64
    p=ANCHORS[:,0,None,:]*(1-u[None,:,None])+ANCHORS[:,1,None,:]*u[None,:,None]
    p[:,:,2]-=.06*np.sin(np.pi*u);old=p.copy()
    a=np.array([i for i in range(65) if i!=36]);b=a+1
    rest=np.linalg.norm(p[:,b]-p[:,a],axis=2)
    weights=np.ones(66);weights[[0,-1]]=0
    broken=np.zeros(3,dtype=bool);breaks=[None]*3;frames=[];events=0;peak=0.
    for step in range(720):
        t=step/120
        py=-1.2+2.7*np.clip((t-1.2)/2.6,0,1) if mode=='forward' else -1.2+.98*max(0,1-abs(t-2.2)) if mode=='retreat' else -2.
        vel=(p-old)*.988;old=p.copy();p+=vel
        p[:,:,2]-=9.81/120**2;p[:,:,1]+=(.6*np.sin(t*2.1+np.arange(66)[None,:]*.18))/120**2
        for iteration in range(40):
            for parity in (0,1):
                aa=a[a%2==parity];bb=aa+1
                delta=p[:,bb]-p[:,aa];length=np.linalg.norm(delta,axis=2)
                corr=delta*((length-rest[:,a%2==parity])/np.maximum(length,1e-9)/(weights[aa]+weights[bb]))[:,:,None]
                p[:,aa]+=corr*weights[aa][None,:,None];p[:,bb]-=corr*weights[bb][None,:,None]
            for k in range(3):
                if not broken[k]:
                    mid=(p[k,36]+p[k,37])/2;p[k,36]=mid;p[k,37]=mid
            if contact:
                for j,k in [(0,2),(2,1),(0,1)]:
                    delta=p[j,:,None,:]-p[k,None,:,:]
                    # Neighbouring centreline samples represent ribbon footprints.
                    # The short depth radius keeps overlapping tape visibly thin.
                    mask=(delta[:,:,0]**2+delta[:,:,2]**2<.055**2)&(np.abs(delta[:,:,1])<.006)
                    ia,ib=np.nonzero(mask)
                    if len(ia):
                        events+=len(ia)
                        dy=delta[ia,ib,1];sign=np.where(dy>0,1.,-1.)
                        sign[np.abs(dy)<1e-8]=-1.
                        correction=sign*(.006-np.abs(dy))*.5
                        change_a=np.zeros(66);change_b=np.zeros(66)
                        np.add.at(change_a,ia,correction);np.add.at(change_b,ib,-correction)
                        p[j,:,1]+=np.clip(change_a,-.006,.006)*weights
                        p[k,:,1]+=np.clip(change_b,-.006,.006)*weights
            for tx in [-1.8,1.8]:
                dx=p[:,:,0]-tx;dy=p[:,:,1];r=np.hypot(dx,dy);mask=r<.23
                p[:,:,0]=np.where(mask,tx+dx/np.maximum(r,1e-9)*.23,p[:,:,0]);p[:,:,1]=np.where(mask,dy/np.maximum(r,1e-9)*.23,p[:,:,1])
            dx=p[:,:,0]-.12;dy=p[:,:,1]-py;r=np.hypot(dx,dy);mask=(r<.31)&(p[:,:,2]>.5)&(p[:,:,2]<1.8)
            p[:,:,0]=np.where(mask,.12+dx/np.maximum(r,1e-9)*.31,p[:,:,0]);p[:,:,1]=np.where(mask,py+dy/np.maximum(r,1e-9)*.31,p[:,:,1])
            p[:,:,2]=np.maximum(p[:,:,2],.05);p[:,0]=ANCHORS[:,0];p[:,-1]=ANCHORS[:,1]
        for k in range(3):
            if not broken[k] and p[k,36,1]>ANCHORS[k,0,1]+.36:
                broken[k]=True;breaks[k]=step//5+1
        if step%5==4:
            frames.append(p.tolist());peak=max(peak,float(np.max(np.abs(np.linalg.norm(p[:,b]-p[:,a],axis=2)-rest))))
    assert np.isfinite(p).all()
    assert all(v is not None for v in breaks) if mode=='forward' else all(v is None for v in breaks)
    return {'frames':frames,'break_frames':breaks,'contact_projections':events,'max_link_error_m':peak}
if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    coupled=run();free=run(contact=False);retreat=run('retreat');idle=run('idle')
    difference=float(np.max(np.linalg.norm(np.array(coupled['frames'])-np.array(free['frames']),axis=3)))
    assert difference>.001 and coupled['contact_projections']>0
    (OUT/'motion.json').write_text(json.dumps(coupled,separators=(',',':')))
    (OUT/'physics_check.json').write_text(json.dumps({'anchors':ANCHORS.tolist(),'break_frames':coupled['break_frames'],'retreat_break_frames':retreat['break_frames'],'idle_break_frames':idle['break_frames'],'contact_projections':coupled['contact_projections'],'max_difference_from_contact_disabled_m':difference,'max_link_error_m':coupled['max_link_error_m'],'limitation':'Anisotropic centreline contact proxies; no full surface friction or continuous cloth collision.'},indent=2))
    print((OUT/'physics_check.json').read_text())
