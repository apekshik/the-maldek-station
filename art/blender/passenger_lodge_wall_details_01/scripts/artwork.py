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
  if (self.name.startswith(('poster_','notice_')) and self.name!='notice_header') or self.name=='timetable':
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
# Three complementary screenprint-style travel illustrations; geography is decorative fiction.
for i,title,sub in [(1,'SKI MALDEK','MAKE A DAY OF IT'),(2,'ABOVE THE PINES','TRAVEL BY GONDOLA'),(3,'THE LONG VIEW','TAKE TIME TO WALK')]:
 a=Art('poster_'+str(i),1400,2000,physical=(.69,.99));a.text(90,70,'MALDEK  /  VISITOR SERIES',30,BLUE,'bold');a.text(90,140,title,81,GREEN,'serif');a.rect(90,264,1220,1435,[BLUE,GOLD,GREEN][i-1]);a.circle(1070,480,125,GOLD if i!=2 else CREAM)
 a.poly([(90,1020),(405,580),(652,942),(855,660),(1310,1110),(1310,1699),(90,1699)],'#cbd1be')
 a.poly([(90,1260),(405,580),(492,995),(652,942),(855,660),(940,1040),(1310,1200),(1310,1699),(90,1699)],'#8baba1')
 a.poly([(90,1330),(560,1040),(830,1190),(1310,975),(1310,1699),(90,1699)],CREAM if i==1 else '#447368')
 for x,y,h in [(170,1190,280),(1120,1220,315),(1230,1330,250),(235,1440,185)]:
  a.poly([(x,y-h),(x-h*.27,y),(x+h*.27,y)],GREEN if i!=3 else '#183b36');a.rect(x-5,y,10,35,GREEN)
 if i==1:
  a.line([(410,1340),(780,1400),(1010,1560),(900,1630)],GOLD,12);a.circle(728,1080,34,INK);a.poly([(690,1114),(748,1090),(822,1185),(757,1230),(680,1190)],GOLD);a.line([(724,1200),(651,1280),(765,1302)],INK,24);a.line([(779,1210),(842,1265),(886,1250)],INK,22);a.line([(570,1285),(942,1350)],RED,13);a.line([(803,1160),(958,1300)],INK,6)
 elif i==2:
  a.line([(90,650),(1310,915)],INK,9);a.line([(740,790),(740,900)],INK,15);a.rect(575,915,340,280,BLUE);a.poly([(575,915),(600,875),(890,875),(915,915)],INK);a.rect(605,935,123,130,CREAM);a.rect(753,935,132,130,CREAM);a.line([(745,931),(745,1185)],GOLD,5);a.rect(605,1100,280,10,GOLD)
 else:
  a.line([(930,1660),(740,1510),(870,1400),(615,1260)],GOLD,32)
  for x,y,scale in [(635,1290,1),(750,1325,.8)]:
   a.circle(x,y-90*scale,23*scale,CREAM);a.rect(x-22*scale,y-63*scale,44*scale,80*scale,GOLD);a.line([(x-12*scale,y+10*scale),(x-35*scale,y+85*scale)],INK,15);a.line([(x+14*scale,y+10*scale),(x+40*scale,y+80*scale)],INK,15)
 a.text(90,1760,sub,46,GREEN,'bold');a.text(90,1850,'A little further from the everyday.',37,BLUE,'serif');a.text(90,1940,'REGIONAL TRAVEL  /  ILLUSTRATED EDITION',23,BLUE);a.save()
# Accurate relative station diagram, directly using surveyed world coordinates.
a=Art('visitor_map',1800,1450,physical=(1.38,1.12));a.text(85,65,'MALDEK STATION',82,GREEN,'bold');a.text(85,167,'Visitor routes',54,BLUE,'serif');a.text(85,247,'Platform level  /  diagram of the station buildings',30)
def xy(x,y):return (100+(x+25)*48,410+(7-y)*39)
def building(x0,y0,x1,y1,color):
 x,y=xy(x0,y1);xx,yy=xy(x1,y0);a.rect(x,y,xx-x,yy-y,color)
building(-24.1,-7.2,-10.1,4,'#d7d4bc');building(-24.1,-12.2,-19.1,-7.2,'#afc2b7');building(-16.1,-13.2,-10.1,-7.2,'#afc2b7');building(-8.1,-5.3,-2.1,.1,BLUE)
# exterior platform band and gondola boarding location
building(-24.1,4,1.3,5.1,'#b3c6c4');a.line([xy(-17.1,-4),xy(-17.1,5),xy(-3.3,5),xy(-3.3,.2)],GOLD,15);a.line([xy(-3.3,5),xy(0,5)],GOLD,15)
a.line([xy(-17.1,-12.6),xy(-17.1,-7.2),xy(-17.1,-4)],GREEN,9)
x,y=xy(-17.1,-4);a.circle(x,y,15,RED)
a.text(*xy(-23,1.5),'PASSENGER LODGE',29,GREEN,'bold');a.text(*xy(-23,.2),'Six-table waiting room',24)
a.text(*xy(-23,-8),'COFFEE',25,GREEN,'bold');a.text(*xy(-15.7,-8),'RESTROOMS',23,GREEN,'bold');a.text(*xy(-7.7,-1),'CONTROL',27,CREAM,'bold');a.text(*xy(-7.7,-2.3),'Staff only',23,CREAM)
a.text(100,348,'PUBLIC PLATFORM',25,BLUE,'bold');a.text(1240,320,'GONDOLA',28,BLUE,'bold');a.line([(1320,365),xy(0,5)],BLUE,3);a.text(1240,600,'Independent entrance',25,BLUE);a.text(1240,640,'Use the exterior platform.',25);a.line([(1240,588),xy(-3.3,.2)],BLUE,3)
a.text(470,1230,'ARRIVAL COURT',24,GREEN,'bold');a.line([(100,1310),(170,1310)],GOLD,12);a.text(190,1290,'Exterior route to control and gondola',26);a.circle(940,1310,12,RED);a.text(970,1290,'Lodge reference point',26);a.text(100,1380,'Station plan only. Ask the attendant for current piste and weather information.',27);a.save()
a=Art('timetable',1400,1900,physical=(.78,1.10));a.rect(0,0,1400,305,BLUE);a.text(90,70,'MALDEK',92,CREAM,'bold');a.text(90,190,'GONDOLA INFORMATION',43,CREAM,'bold');a.text(90,375,'Departure board',67,GREEN,'serif');a.text(90,478,'Check with the attendant before boarding.',35);a.line([(90,570),(1310,570)],GREEN,4)
for row,(l,r) in enumerate([('FIRST DEPARTURE','09:00'),('REGULAR SERVICE','Every 30 minutes'),('LAST DEPARTURE','16:30')]):
 y=650+row*180;a.text(90,y,l,32,BLUE,'bold');a.text(90,y+58,r,57,GREEN,'serif');a.line([(90,y+139),(1310,y+139)],'#b4b5a2',2)
a.text(90,1250,'Before you travel',48,GREEN,'serif')
for j,t in enumerate(['Have your pass ready.','Keep the boarding gate clear.','Follow the attendant\'s instructions.']):a.text(90,1340+65*j,t,37)
a.rect(90,1580,1220,182,'#ddd3b5');a.text(130,1612,'WEATHER NOTE',31,RED,'bold');a.text(130,1664,'Afternoon excursion cancelled.',37);a.text(90,1820,'Printed schedule  /  subject to operating conditions',28);a.save()
# Community paper set; ordinary content and no cipher.
notices=[('club','SKI CLUB',['Weekend outings','All abilities welcome.','Leave your name','with the attendant.'],GREEN),('lost','LOST PROPERTY',['Missing a glove?','Ask at the coffee hatch.','Please describe','the item you lost.'],BLUE),('hours','COFFEE HATCH',['Open with the','passenger lodge.','Tea, coffee','and light snacks.'],GREEN),('walk','WEEKEND WALK',['A gentle local outing.','Meet at the lodge.','Ask for details','at the coffee hatch.'],RED),('weather','WEATHER UPDATE',['Afternoon excursion','cancelled.','Please ask about','the next outing.'],BLUE)]
for name,title,lines,c in notices:
 a=Art('notice_'+name,700,850,'#e9dfbe' if name=='weather' else CREAM,physical=(.27,.328));a.text(55,72,title,42,c,'bold');a.line([(55,143),(645,143)],c,5)
 for i,t in enumerate(lines):a.text(55,235+i*100,t,36,INK,'serif')
 a.text(55,750,'MALDEK  /  COMMUNITY',22,c);a.save()
for name,txt,sub,w,h in [('notice_header','COMMUNITY','LOCAL NOTICES',1400,160),('restrooms','RESTROOMS','',1400,250),('women','WOMEN','',900,230),('men','MEN','',900,230),('exit','PUBLIC EXIT','ARRIVAL COURT',1400,300),('boarding','GONDOLA','PLATFORM EXIT',1400,300),('staff','STAFF ONLY','COFFEE PREPARATION',1400,300),('lost_property','LOST PROPERTY','',1600,200)]:
 a=Art(name,w,h,BLUE if name in ['boarding','staff'] else GREEN);a.text(w/2,28,txt,int(h*.37),CREAM,'bold','middle')
 if sub:a.text(w/2,h*.68,sub,int(h*.16),CREAM,'sans','middle')
 a.save()
a=Art('menu',3150,540,GREEN,physical=(2.07,.355));a.text(80,55,'THE COFFEE HATCH',90,CREAM,'serif');a.line([(80,200),(3070,200)],GOLD,4)
for x,title,sub in [(80,'COFFEE & TEA','Freshly made'),(1120,'HOT CHOCOLATE','A warm stop'),(2210,'SOUP & SNACKS','Ask what is available')]:a.text(x,260,title,62,CREAM,'bold');a.text(x,365,sub,51,CREAM,'serif')
a.save()
a=Art('clock_face',1400,1400,physical=(.33,.33));a.circle(700,700,695,CREAM)
for i in range(60):
 angle=i*math.tau/60;r=585 if i%5 else 550;a.line([(700+math.sin(angle)*r,700-math.cos(angle)*r),(700+math.sin(angle)*620,700-math.cos(angle)*620)],INK,8 if i%5 else 17)
for i in range(1,13):
 angle=i*math.tau/12;a.text(700+math.sin(angle)*455,650-math.cos(angle)*455,str(i),90,GREEN,'sans','middle')
a.text(700,900,'MALDEK',36,GREEN,'bold','middle');a.save()
(A/'inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf8')
# Wall elevation planning sheet, dimensions measured from the material master.
a=Art('wall_elevations',2200,1500,'#f5f0e1');a.text(75,60,'PASSENGER LODGE / WALL DISPLAY SURVEY',59,GREEN,'bold');a.text(75,145,'Metres  /  floor +4.00 m  /  source hash b9d78ed0...',32)
a.text(75,240,'WEST WALL  /  depth 0 to 11.2 m',38,BLUE,'bold');a.rect(75,330,2016,576,'#dadacb');a.line([(75,906),(2091,906)],INK,4)
for d in range(12):
 x=75+d*180;a.line([(x,910),(x,925)],INK,2);a.text(x,945,str(d),25)
for name,d,w,h,z in [('POSTER 1',2.575,.75,1.05,1.675),('POSTER 2',4.575,.75,1.05,1.675),('POSTER 3',6.575,.75,1.05,1.675),('COMMUNITY',8.8,1.55,1.1,1.66)]:
 x=75+(d-w/2)*180;y=906-(z+h/2)*180;a.rect(x,y,w*180,h*180,GREEN);a.text(x,y-42,name,25,BLUE)
a.text(75,1050,'NORTH PIER',32,BLUE,'bold');a.text(75,1110,'Timetable 0.84 x 1.16; centre Z 5.65',29);a.text(75,1160,'Solid pier X -18.90 to -17.70; inset >= 0.18',27)
a.text(1110,1050,'EAST WALL',32,BLUE,'bold');a.text(1110,1110,'Visitor map 1.44 x 1.18; centre Z 5.68',29);a.text(1110,1160,'Centre Y 0.40; no east-wall openings',27)
a.text(75,1280,'Headers: restrooms / public exit / platform / staff. No door-leaf ownership.',30);a.text(75,1360,'Menu and cubby label fit delivered PLK frames. Optional coat hooks omitted to preserve blank wall.',30);a.save()
print('Artwork complete',len(inventory))
