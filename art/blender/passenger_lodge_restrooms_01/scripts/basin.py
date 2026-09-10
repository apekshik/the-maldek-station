"""Rounded rectangular vitreous basin, same 510 x 620 mm bounding envelope."""
import math

def build_basin(mesh,W,n,cx,dd,sign,material):
    # Closed shell: underside, outer wall, rolled rim, inner wall, sloped floor, drain throat.
    # (half projection, half width, corner radius, local z, forward offset, grime)
    rings=[(.028,.028,.028,.660,0,.65),(.15,.205,.085,.675,0,.10),
           (.247,.302,.072,.813,0,.08),(.255,.310,.075,.850,0,.12),
           (.252,.307,.074,.871,0,.25),(.242,.297,.071,.876,0,.40),
           (.185,.257,.065,.872,.030,.75),(.179,.251,.068,.854,.030,.90),
           (.163,.234,.075,.812,.027,.25),(.115,.175,.075,.752,.016,.25),
           (.055,.076,.045,.731,0,.65),(.028,.028,.028,.730,0,1.0)]
    verts=[];weights=[];N=64
    for hx,hy,r,z,off,dirt in rings:
        for quadrant in range(4):
            a0=quadrant*math.pi/2
            sx=1 if quadrant in (0,3) else -1;sy=1 if quadrant<2 else -1
            for j in range(16):
                a=a0+j*math.pi/32
                u=sx*(hx-r)+r*math.cos(a);v=sy*(hy-r)+r*math.sin(a)
                verts.append(W((cx+sign*(u+off),dd+v,z)));weights.append(dirt)
    faces=[]
    for i in range(len(rings)):
        for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,((i+1)%len(rings))*N+(j+1)%N,((i+1)%len(rings))*N+j))
    ob=mesh(n+'_Basin_bowl',verts,faces,material)
    attr=ob.data.attributes.new('PLR_Deposit','FLOAT','POINT')
    for d,w in zip(attr.data,weights):d.value=w
    ob['form']='Rounded rectangle 620 x 510 mm; 75 mm outer corner radius; integrated rear tap deck'
    return ob
