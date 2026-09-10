"""Metre-space local soil envelope; unchanged beyond two explicit masks."""
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def height(old,x,y):
 # Extend the existing shoulder beneath the west promenade, fading outwards.
 west=smooth((x+33)/3.4)*(1-smooth((x+24.1)/.5))*smooth((y+16.3)/1.15)*(1-smooth((y-7.35)/2))
 z=old+max(0,3.48-old)*west
 # Recess only the new stair corridor. Its original lower approach stays fixed.
 cut=smooth((x+9.6)/.75)*(1-smooth((x+5.8)/.75))*smooth((y+16.5)/.8)*(1-smooth((y+7.75)/.55))
 target=max(-.26,min(3.7,(y+14.42)*(4/6.72)-.30))
 return z-max(0,z-target)*cut
