"""Lower only the old terrain underlay beneath the new service route and rooms."""
from PIL import Image
from pathlib import Path
import json
out=Path(__file__).resolve().parents[1]/'revision11';g=json.loads((out/'terrain_grid.json').read_text());im=Image.open(out.parent/'revision10/landscape_canyon.png').convert('RGBA');pix=im.load();origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];n=0
for py in range(1520,1600):
 for px in range(550,650):
  x=(origin[0]-(-105812+px*100))/100;y=((-138209+py*100)-origin[1])/100
  if not (4<x<43 and -32<y<4):continue
  i=round(x-g['xmin']);j=round(y-g['ymin']);z=g['vertices'][j*g['nx']+i][2]-.6;r,green,b,a=pix[px,py];old=r*256+green;h=max(0,min(65535,round(32768+(origin[2]+100*z-23763)*128/100)))
  if h<old:pix[px,py]=(h//256,h%256,b,255);n+=1
im.save(out/'landscape_canyon.png');(out/'landscape_edit.json').write_text(json.dumps({'changed_pixels':n}))
