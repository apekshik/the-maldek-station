"""Independent route clearance and pixel-boundary checks before Unreal import."""
import json,math,sys
from pathlib import Path
from PIL import Image,ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import weight,shoulder
b=Path(__file__).resolve().parents[1];out=b/'gorge'
old={(x,y):z for x,y,z in json.loads((b/'forest_refine/terrain_grid.json').read_text())['vertices']}
new={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
unchanged=0
for (x,y),z in old.items():
 if weight(x,y)==0:assert new[x,y]==z;unchanged+=1
def interp(g,x,y):
 i=math.floor(x*2)/2;j=math.floor(y*2)/2
 for step in [.5,1.]:
  if step==1:i=math.floor(x);j=math.floor(y)
  if all(k in g for k in [(i,j),(i+step,j),(i,j+step),(i+step,j+step)]):
   u=(x-i)/step;v=(y-j)/step
   return (1-v)*((1-u)*g[i,j]+u*g[i+step,j])+v*((1-u)*g[i,j+step]+u*g[i+step,j+step])
 return None
layout=json.loads((b.parents[1]/'blender/visual_fidelity_07/layout.json').read_text());errors=[];checked=0
for route in layout['routes']:
 for x,y,z in route['points']:
  a=interp(old,x,y);c=interp(new,x,y)
  if a is None or c is None:continue
  checked+=1
  if c>a+.01 and c>z-.08:errors.append([route['name'],x,y,z,a,c])
assert not errors,errors
before=Image.open(out/'landscape_before.png').convert('RGBA');after=Image.open(out/'landscape_gorge.png').convert('RGBA');assert before.size==after.size
o=json.loads((out/'before.json').read_text())['origin'];report=json.loads((out/'heightmap_report.json').read_text())
diff=ImageChops.difference(before,after);bbox=diff.convert('RGB').getbbox();assert bbox
count=0
for py in range(bbox[1],bbox[3]):
 for px in range(bbox[0],bbox[2]):
  if before.getpixel((px,py))==after.getpixel((px,py)):continue
  x=(o[0]-(-105812+px*100))/100;y=(-138209+py*100-o[1])/100
  assert weight(x,y)>0;count+=1
assert count==report['changed_pixels']
result={'passed':True,'unchanged_mesh_vertices':unchanged,'route_samples':checked,'new_route_obstructions':errors,'changed_heightmap_pixels':count,'outside_mask_changes':0}
(out/'offline_verification.json').write_text(json.dumps(result,indent=2));print(result)
