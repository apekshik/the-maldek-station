"""Offline heightmap edit, preserving all pixels outside the valley mask."""
import json,math,hashlib,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from forest_refine_shape import height
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
g={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 return (1-v)*((1-u)*g[i,j]+u*g[i+1,j])+v*((1-u)*g[i,j+1]+u*g[i+1,j+1])
before=Image.open(out/'landscape_before.png').convert('RGBA');after=before.copy();pix=after.load();changes=[];bounds=[99999,99999,0,0]
for py in range(before.height):
 y=(-138209+py*100-o[1])/100
 if not -12<y<650:continue
 for px in range(before.width):
  x=(o[0]-(-105812+px*100))/100
  if not -340<x<340:continue
  r,green,blue,alpha=pix[px,py];old=r*256+green;z=(23763+(old-32768)*100/128-o[2])/100
  target=height(z,x,y)
  if -96<=x<112 and -80<=y<96:target=min(target,ground(x,y)-.8)
  desired=max(old,min(65535,round(32768+(o[2]+100*target-23763)*128/100)))
  if desired>old:
   pix[px,py]=(desired//256,desired%256,blue,alpha);changes.append([px,py,old,desired]);bounds=[min(bounds[0],px),min(bounds[1],py),max(bounds[2],px),max(bounds[3],py)]
after.save(out/'landscape_valley.png')
report={'changed_pixels':len(changes),'pixel_bounds':bounds,'local_mask':[-340,340,-12,650],'outside_mask_changes':0,'only_raises_ground':True,'source_sha256':hashlib.sha256((out/'landscape_before.png').read_bytes()).hexdigest(),'result_sha256':hashlib.sha256((out/'landscape_valley.png').read_bytes()).hexdigest(),'changes':changes}
(out/'landscape_edit.json').write_text(json.dumps(report));print('VALLEY_HEIGHTMAP',len(changes),bounds,flush=True)
