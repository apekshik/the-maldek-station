"""Check final route clearance and native height preservation outside the edit mask."""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import weight
b=Path(__file__).resolve().parents[1];out=b/'gorge';o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
old={(x,y):z for x,y,z in json.loads((b/'forest_refine/terrain_grid.json').read_text())['vertices']};new={(round(x,3),round(y,3)):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def interp(g,x,y):
 for step in [.5,1.]:
  i=math.floor(x/step)*step;j=math.floor(y/step)*step
  if all(k in g for k in [(i,j),(i+step,j),(i,j+step),(i+step,j+step)]):
   u=(x-i)/step;v=(y-j)/step
   return (1-v)*((1-u)*g[i,j]+u*g[i+step,j])+v*((1-u)*g[i,j+step]+u*g[i+step,j+step])
count=0;errors=[]
for route in json.loads((b.parents[1]/'blender/visual_fidelity_07/layout.json').read_text())['routes']:
 for x,y,z in route['points']:
  a=interp(old,x,y);c=interp(new,x,y)
  if a is None or c is None:continue
  count+=1
  if c>a+.01 and c>z-.08:errors.append([route['name'],x,y,z,a,c])
p=json.loads((out/'native_edge_patch.json').read_text());r=p['bounds'];w=r[2]-r[0]+1;outside=0
for i,(a,c) in enumerate(zip(p['original_merged'],p['desired'])):
 px=r[0]+i%w;py=r[1]+i//w;x=(o[0]+105812)/100-px;y=py-(o[1]+138209)/100
 if not weight(x,y):
  outside+=1
  if a!=c:errors.append(['outside mask',px,py,a,c])
assert not errors,errors
result={'passed':True,'route_samples':count,'outside_mask_samples_unchanged':outside,'route_obstructions':errors,'perimeter':json.loads((out/'edge_blend.json').read_text())};(out/'final_offline_verification.json').write_text(json.dumps(result,indent=2));print(result)
