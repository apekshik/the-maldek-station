"""Original deterministic artwork: matching editable SVG and unlit PNG outputs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html,json,math,random
P=Path(__file__).resolve().parents[1]; A=P/'artwork';T=P/'textures'; A.mkdir(exist_ok=True);T.mkdir(exist_ok=True)
CREAM='#eee5cc';GREEN='#254d43';BLUE='#254a5b';GOLD='#c99542';INK='#283833';RED='#965844'
inventory=[]
class Art:
 def __init__(self,name,w,h,bg=CREAM,physical=None):
  self.name=name;self.w=w;self.h=h;self.im=Image.new('RGB',(w,h),bg);self.d=ImageDraw.Draw(self.im);self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'];self.texts=[];self.physical=physical or {'notice_header':(1.4,.12),'restrooms':(1.026,.206),'women':(.666,.166),'men':(.666,.166),'exit':(1.046,.236),'boarding':(1.026,.236),'staff':(.806,.196),'lost_property':(.44,.055)}.get(name);self.rect(0,0,w,h,bg)
 def rect(self,x,y,w,h,c):
  self.d.rectangle((x,y,x+w,y+h),fill=c);self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>')
 def poly(self,pts,c):
  self.d.polygon(pts,fill=c);self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{c}"/>')
 def line(self,pts,c=INK,width=3):
  self.d.line(pts,fill=c,width=width,joint='curve');self.svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{c}" stroke-width="{width}" stroke-linejoin="round"/>')
 def circle(self,x,y,r,c):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=c);self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
 def text(self,x,y,s,size=32,c=INK,font='sans',anchor='start'):
  fname='georgia.ttf' if font=='serif' else ('arialbd.ttf' if font=='bold' else 'arial.ttf');f=ImageFont.truetype('C:/Windows/Fonts/'+fname,size)
  width=self.d.textlength(s,font=f); xx=x-width/2 if anchor=='middle' else (x-width if anchor=='end' else x)
  self.d.text((xx,y),s,fill=c,font=f,anchor='lt');self.svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" text-anchor="{anchor}" font-family="{("Georgia" if font=="serif" else "Arial")}" font-weight="{("700" if font=="bold" else "400")}" font-size="{size}" fill="{c}">{html.escape(s)}</text>');self.texts.append(s)
 def save(self):
  if (self.name.startswith(('safety','archive','leaflet')) and self.name!='notice_header') or self.name=='timetable':
   rng=random.Random(sum(ord(c) for c in self.name))
   # Editable vector age marks confined to handling margins, no lighting baked in.
   for i in range(140):
    x=rng.choice([rng.uniform(5,22),rng.uniform(self.w-22,self.w-5)]);y=rng.uniform(20,self.h-20)
    self.circle(x,y,rng.uniform(.3,1.1),'#c9b995')
   for i in range(8):
    y=rng.uniform(50,self.h-50);self.line([(3,y),(rng.uniform(8,16),y+rng.uniform(-2,2))],'#c5b18a',1)
  if self.name=='timetable':
   # Faint tea ring restricted to lower-right margin, clear of text.
   pts=[(self.w-30+42*math.cos(t*math.tau/55),self.h-118+42*math.sin(t*math.tau/55)) for t in range(56)]
   self.line(pts,'#cfbd96',3)
  (A/(self.name+'.svg')).write_text('\n'.join(self.svg+['</svg>']),encoding='utf8');self.im.save(T/(self.name+'.png'));inventory.append(dict(id=self.name,svg='artwork/'+self.name+'.svg',texture='textures/'+self.name+'.png',pixels=[self.w,self.h],metres=self.physical,text=self.texts,provenance='Original vector illustration and deterministic typesetting authored for this package; no external artwork',texels_per_metre=[round(self.w/self.physical[0]),round(self.h/self.physical[1])] if self.physical else None))
# Original restrained illustrated guidance; advisory dressing, no gameplay rule.
a=Art('safety',1280,1780,physical=(.64,.89));a.rect(0,0,1280,270,GREEN);a.text(75,55,'SHARE THE MOUNTAIN',61,CREAM,'bold');a.text(75,150,'A little care goes a long way',41,CREAM,'serif')
for i,(title,lines) in enumerate([('LOOK AHEAD',['Give others room.','Check before setting off.']),('TAKE YOUR TIME',['Choose a comfortable pace.','Rest clear of the route.']),('LEAVE IT AS YOU FOUND IT',['Take litter back with you.','Respect the mountain.'])]):
 y=350+i*420;a.circle(150,y+80,83,GOLD);a.text(295,y+5,title,40,GREEN,'bold')
 for j,t in enumerate(lines):a.text(295,y+95+j*67,t,38)
 # Small deterministic ski / landscape line illustration.
 if i==0:
  a.circle(136,y+50,10,CREAM);a.line([(136,y+65),(154,y+90),(180,y+100)],CREAM,8);a.line([(112,y+116),(190,y+127)],CREAM,5)
 if i==1:a.line([(90,y+114),(125,y+59),(145,y+89),(170,y+46),(210,y+114)],CREAM,5)
 if i==2:a.line([(125,y+47),(133,y+118),(177,y+118),(184,y+47),(125,y+47)],CREAM,5)
 a.line([(75,y+318),(1205,y+318)],'#c3c1a5',2)
a.text(75,1670,'MALDEK  /  VISITOR GUIDANCE',30,BLUE,'bold');a.save()
# Original monochrome studies, explicitly not historical documentary photographs.
for i in [1,2]:
 a=Art('archive_'+str(i),1800,1230,'#e5dfcf',physical=(.49,.34));a.rect(70,60,1660,980,'#adb0a6')
 a.poly([(70,640),(320,370),(510,570),(850,180),(1170,510),(1450,290),(1730,680),(1730,1040),(70,1040)],'#727d78')
 a.poly([(70,865),(450,640),(780,735),(1130,590),(1730,900),(1730,1040),(70,1040)],'#475953')
 for x,y in [(150,810),(230,870),(1450,910),(1550,970),(1620,840)]:a.poly([(x,y-190),(x-65,y),(x+65,y)],'#34423e')
 if i==1:
  a.rect(450,600,735,295,'#d0cebf');a.poly([(410,610),(580,500),(1190,500),(1280,610)],'#3c4b46')
  for x in [490,690,900]:a.rect(x,655,115,115,'#52635c');a.line([(x+57,655),(x+57,770)],'#b7bfb5',6)
  a.rect(1060,655,75,240,'#53645c');a.line([(320,938),(1390,938)],'#b4beb6',10)
  for x in range(350,1400,95):a.line([(x,940),(x,870)],'#b4beb6',8)
 else:
  a.line([(75,325),(1730,590)],'#303e39',7);a.line([(690,425),(690,530)],'#303e39',13);a.poly([(565,530),(805,530),(835,560),(825,750),(550,750),(540,560)],'#d0cebf')
  for x in [565,650,735]:a.rect(x,565,66,95,'#53625c')
  a.line([(1440,545),(1340,1010)],'#273d35',19);a.line([(1510,550),(1580,1030)],'#273d35',19);a.line([(1270,507),(1610,563)],'#273d35',16)
 a.text(80,1090,'PLATFORM STUDY' if i==1 else 'ABOVE THE TREE LINE',44,INK,'serif');a.text(80,1170,'MALDEK  /  ILLUSTRATED COLLECTION',23,BLUE);a.save()
for name,title,sub,c in [('routes','A DAY OUT','Ask for local routes',GREEN),('lodge','AT THE LODGE','Visitor information',BLUE),('care','MOUNTAIN CARE','Small things matter',RED)]:
 a=Art('leaflet_'+name,680,820,CREAM,physical=(.17,.205));a.rect(0,0,680,165,c);a.text(40,40,title,43,CREAM,'bold');a.text(40,202,sub,31,c,'serif');a.poly([(40,560),(210,300),(340,505),(485,360),(640,565),(640,705),(40,705)],c);a.text(40,755,'MALDEK',28,c,'bold');a.save()
a=Art('rack_label',1400,150,GREEN,physical=(.39,.04));a.text(700,25,'TAKE A LEAFLET',80,CREAM,'bold','middle');a.save()
a=Art('first_aid',1120,1260,CREAM,physical=(.31,.35));a.rect(340,180,440,440,GREEN);a.rect(508,220,104,360,CREAM);a.rect(380,348,360,104,CREAM);a.text(560,760,'FIRST AID',125,GREEN,'bold','middle');a.text(560,1015,'MALDEK',49,GREEN,'sans','middle');a.save()
for typ,title,values,unit in [('temperature','TEMPERATURE',[-10,0,10,20,30],'°C'),('humidity','RELATIVE HUMIDITY',[20,35,50,65,80],'% RH')]:
 a=Art('gauge_'+typ,1000,1000,CREAM,physical=(.14,.14));a.text(500,715,title,typ=='temperature' and 39 or 31,GREEN,'bold','middle')
 for j in range(41):
  ang=math.radians(-125+j*250/40);r=350 if j%10 else 325;a.line([(500+math.sin(ang)*r,535-math.cos(ang)*r),(500+math.sin(ang)*390,535-math.cos(ang)*390)],INK,4 if j%10 else 10)
 for j,val in enumerate(values):
  ang=math.radians(-125+j*62.5);a.text(500+math.sin(ang)*257,500-math.cos(ang)*257,str(val),59,INK,'sans','middle')
 a.text(500,790,unit,65,GREEN,'serif','middle');a.save()
for name,title in [('A','PLATFORM STUDY'),('B','ABOVE THE TREE LINE')]:
 a=Art('caption_'+name,1400,146,'#e5dfcf',physical=(.464,.04));a.text(700,28,title,67,BLUE,'serif','middle');a.save()
(A/'inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf8')
# Elevation measured in source-world metres (Y runs rightward as -Y).
a=Art('elevation',2400,1100,'#f1ecd9');a.text(80,45,'EAST WALL / ADDITIVE DISPLAY PACKAGE',56,GREEN,'bold');a.text(80,125,'Floor Z 4.00 m  |  facing -X  |  source bcf7e630...  |  existing map and lockers retained',29)
scale=240;left=90;base=920
def panel(y,z,w,h,color,label):
 x=left+(1.6-y-w/2)*scale;yy=base-(z-4+h/2)*scale;a.rect(x,yy,w*scale,h*scale,color);a.text(x,yy-29,label,22,INK);a.text(x,yy+h*scale+8,f'{w:.2f} x {h:.2f} m',18,INK)
a.rect(left,210,2150,710,'#d7d6c4');a.rect(left,base-1.05*scale,2150,1.05*scale,'#869788');a.line([(left,base-1.05*scale),(2240,base-1.05*scale)],GREEN,8)
panel(.4,5.68,1.44,1.18,BLUE,'EXISTING MAP')
for name,y,z,w,h in [('SAFETY',-1.12,5.78,.7,.95),('ARCHIVE A',-2.10,6.10,.55,.4),('ARCHIVE B',-2.40,5.46,.55,.4),('LEAFLETS',-3.23,5.18,.45,.6),('GAUGE',-4.03,5.91,.22,.35),('FIRST AID',-5.02,5.61,.38,.45)]:panel(y,z,w,h,GOLD,name)
panel(-6.8,4.925,.5,1.85,BLUE,'LOCKER CORNER')
a.text(90,980,'Dado Z 5.03–5.07: rack back clears trim by 30 mm; no trim changes.',28);a.text(90,1035,'Six new roots. Mixed heights preserve open upper wall. Coordinates and full matrices: placement_manifest.json.',27);a.save()
print('Artwork',len(inventory))
