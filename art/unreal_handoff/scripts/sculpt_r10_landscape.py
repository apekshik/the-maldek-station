"""Match the Gaea landscape underlay to the new canyon and approach mesh."""
from PIL import Image
import json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';s=json.loads((out/'terrain_grid.json').read_text());vs=s['vertices'];nx=s['nx'];ny=len(vs)//nx
im=Image.open(out.parent/'revision06/landscape_cliff.png').convert('RGBA');pix=im.load();origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];changed=0
for py in range(1450,2070):
 for px in range(320,880):
  x=(origin[0]-(-105812+px*100))/100;y=((-138209+py*100)-origin[1])/100
  r,g,b,a=pix[px,py];old=r*256+g;z=None
  if s['xmin']<=x<s['xmax'] and s['ymin']<=y<s['ymax']:
   ix=int(x-s['xmin']);iy=int(y-s['ymin']);u=x-s['xmin']-ix;v=y-s['ymin']-iy
   z=vs[iy*nx+ix][2]*(1-u)*(1-v)+vs[iy*nx+ix+1][2]*u*(1-v)+vs[(iy+1)*nx+ix][2]*(1-u)*v+vs[(iy+1)*nx+ix+1][2]*u*v-.6
  elif 35<y<430 and abs(x)<250:
   w=min(1,(y-35)/35,(430-y)/70,(250-abs(x))/60);w=max(0,w);w=w*w*(3-2*w)
   oldz=((old-32768)*100/128+23763-origin[2])/100;z=oldz*(1-w)+(-155+12*math.sin(x*.025)*math.cos(y*.035))*w
  if z is None:continue
  target=max(0,min(65535,round(32768+(origin[2]+z*100-23763)*128/100)))
  if target<old:pix[px,py]=(target//256,target%256,b,255);changed+=1
im.save(out/'landscape_canyon.png');(out/'landscape_edit.json').write_text(json.dumps({'lowered_pixels':changed,'gorge_depth_m':145,'far_gorge_extent_m':430},indent=2))
