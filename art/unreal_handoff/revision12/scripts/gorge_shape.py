"""Local cliff shoulder; distant Gaia composition and occupied routes are fixed."""
import math
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def lip(x):return 10+24*smooth((x-16)/23)+1.5*math.sin(x*.15)
def cliff_weight(x,y):
 return smooth((x+96)/24)*(1-smooth((x-76)/35))*smooth((y+2)/8)*(1-smooth((y-100)/70))
def shoulder(x,y):
 return smooth((x+26)/1.8)*(1-smooth((x+5.4)/1.4))*smooth((y+15)/1.6)*(1-smooth((y-6.5)/3))
def weight(x,y):return max(cliff_weight(x,y),shoulder(x,y))
def height(old,x,y):
 w=cliff_weight(x,y)
 d=y-lip(x)
 # A short crest, steep broken face, then a descending wooded apron.
 fall=smooth(d/29)
 target=-.35-(67+5*math.sin(x*.11))*fall
 if d>29:target-=18*smooth((d-29)/55)
 target+=fall*1.7*math.sin(x*.32+y*.17)*math.sin(y*.38)
 z=old+(target-old)*w
 # Under the 4 m western deck only: below its 3.72 m slab underside.
 # Stops west of the lower gallery and north of the arrival stair footprint.
 return z+max(0,3.48-z)*shoulder(x,y)
