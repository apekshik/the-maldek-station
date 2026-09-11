def geom(o):
 e=o.evaluated_get(dg);me=e.to_mesh();v=[o.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];e.to_mesh_clear();return v,f

def bounds(v):return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])

def overlaps(a,b):return all(a[0][i]<b[1][i]-1e-5 and b[0][i]<a[1][i]-1e-5 for i in range(3))

def hull(v):
 pts=sorted(set((round(p.x,7),round(p.y,7)) for p in v))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[];upper=[]
 for p in pts:
  while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 for p in reversed(pts):
  while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 return lower[:-1]+upper[:-1]

def polygon_distance(x,y,poly):
 inside=True;distance=999
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx=b[0]-a[0];dy=b[1]-a[1]
  if dx*(y-a[1])-dy*(x-a[0])<0:inside=False
  t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
  distance=min(distance,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return 0 if inside else distance
