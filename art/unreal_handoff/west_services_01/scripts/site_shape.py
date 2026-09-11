def smooth(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
def height(old,x,y):
 # Core lies beneath the platform; blend into the retained hillside outside it.
 west=smooth((x+51)/10.2);east=1-smooth((x+28.9)/.75)
 south=smooth((y+16)/8.3);north=1-smooth((y-10.7)/5.3)
 weight=west*east*south*north
 target=.20+.08*__import__('math').sin(x*.65)*__import__('math').cos(y*.52)
 return old+(target-old)*weight
