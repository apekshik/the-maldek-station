"""Edit current exported heightmap inside a verified local mask only."""
import json,sys,math,hashlib
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import height,weight
b=Path(__file__).resolve().parents[1];out=b/'gorge';o=json.loads((out/'before.json').read_text())['origin']
grid={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 if not all(k in grid for k in [(i,j),(i+1,j),(i,j+1),(i+1,j+1)]):return None
 return (1-v)*((1-u)*grid[i,j]+u*grid[i+1,j])+v*((1-u)*grid[i,j+1]+u*grid[i+1,j+1])
im=Image.open(out/'landscape_before.png').convert('RGBA')
assert im.convert('RGB').getbbox(), 'Rejected blank heightmap export; use native CPU patch'
after=im.copy();p=after.load();changes=[]
for py in range(im.height):
 y=(-138209+py*100-o[1])/100
 if not -15<y<170:continue
 for px in range(im.width):
  x=(o[0]-(-105812+px*100))/100
  if not weight(x,y):continue
  r,g,blue,a=p[px,py];old=r*256+g;z=(23763+(old-32768)*100/128-o[2])/100
  target=height(z,x,y);surface=ground(x,y)
  if surface is not None:target=min(target,surface-.65)
  new=max(0,min(65535,round(32768+(o[2]+100*target-23763)*128/100)))
  if new!=old:p[px,py]=(new//256,new%256,blue,a);changes.append([px,py,old,new])
after.save(out/'landscape_gorge.png')
assert all(weight((o[0]-(-105812+px*100))/100,(-138209+py*100-o[1])/100)>0 for px,py,_,_ in changes)
(out/'heightmap_report.json').write_text(json.dumps({'changed_pixels':len(changes),'outside_mask_changes':0,'mask_local_m':[-96,111,-15,170],'source_sha256':hashlib.sha256((out/'landscape_before.png').read_bytes()).hexdigest(),'changes':changes}))
print('Localized heightmap pixels:',len(changes))
