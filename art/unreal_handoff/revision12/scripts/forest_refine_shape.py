"""Shared metre-space valley profile for the local mesh and distant landscape."""
import math
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def shape(x,y):
 lip=7+24*smooth((x-16)/20)+2*math.sin(x*.085)
 start=-12+30*smooth((x-16)/20)
 centre=-5+35*math.sin(y*.006)
 floor=-91+5*math.sin(y*.025)+4*math.cos(x*.028+y*.017)
 floor+=16*smooth((abs(x-centre)-65)/170)
 if y<180:
  t=smooth((y-lip)/(180-lip));target=-.2+(floor+.2)*t
 else:
  t=smooth((y-180)/420);target=floor*(1-t)+(-35+8*math.sin(x*.006))*t
 edge=smooth((x+340)/115)*(1-smooth((x-225)/115))*(1-smooth((y-570)/80))
 join=smooth((y-start)/(lip-start)) if y<lip else 1
 return target,edge*join if y>start else 0
def height(old,x,y):
 target,weight=shape(x,y);return old+max(0,target-old)*weight
