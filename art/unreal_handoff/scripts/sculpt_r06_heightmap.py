from PIL import Image
import json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';s=json.loads((out/'terrain_grid.json').read_text());v=s['vertices'];nx=s['nx'];im=Image.open(out/'landscape_before.png').convert('RGBA');p=im.load();origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];changed=0
for py in range(1550,1670):
 for px in range(590,637):
  x=(origin[0]-(-105812+px*100))/100;y=((-138209+py*100)-origin[1])/100
  if not (-17<x<19 and 2<y<94):continue
  ix=int(math.floor(x-s['xmin']));iy=int(math.floor(y-s['ymin']));a=x-s['xmin']-ix;b=y-s['ymin']-iy
  z=v[iy*nx+ix][2]*(1-a)*(1-b)+v[iy*nx+ix+1][2]*a*(1-b)+v[(iy+1)*nx+ix][2]*(1-a)*b+v[(iy+1)*nx+ix+1][2]*a*b
  r,g,blue,alpha=p[px,py];old=r*256+g;target=round(32768+((origin[2]+z*100-60)-23763)*128/100)
  if target<old:p[px,py]=(target//256,target%256,blue,255);changed+=1
im.putalpha(255);im.save(out/'landscape_cliff.png');(out/'heightmap_edit.json').write_text(json.dumps({'changed_pixels':changed,'scope':'local gorge only','encoding':'16 bit height in RG','landscape_origin':[-105812,-138209,23763]}))
print('changed',changed)
