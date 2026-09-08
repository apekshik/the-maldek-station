"""Recompute the local native patch from its original CPU baseline, not the edited result."""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import weight,height
b=Path(__file__).resolve().parents[1];out=b/'gorge';o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];original=json.loads((out/'native_probe.json').read_text());edge=json.loads((out/'edge_probe.json').read_text());r=original['bounds'];rw=r[2]-r[0]+1;eb=edge['bounds'];ew=eb[2]-eb[0]+1
grid={(round(x,3),round(y,3)):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 if not all(k in grid for k in [(i,j),(i+1,j),(i,j+1),(i+1,j+1)]):return None
 return (1-v)*((1-u)*grid[i,j]+u*grid[i+1,j])+v*((1-u)*grid[i,j+1]+u*grid[i+1,j+1])
current=[];desired=[];merged=[]
for py in range(r[1],r[3]+1):
 y=py-(o[1]+138209)/100
 for px in range(r[0],r[2]+1):
  x=(o[0]+105812)/100-px;i=(py-r[1])*rw+px-r[0];old=original['merged'][i];now=edge['current'][(py-eb[1])*ew+px-eb[0]];current.append(now)
  if not weight(x,y):new=old
  else:
   oldz=(23763+(old-32768)*100/128-o[2])/100;surface=ground(x,y)
   target=surface-.65*weight(x,y) if surface is not None else height(oldz,x,y)
   new=max(0,min(65535,round(32768+(o[2]+100*target-23763)*128/100)))
  desired.append(new);merged.append(new)
(out/'native_edge_patch.json').write_text(json.dumps({'source':'native CPU height data','bounds':r,'layer':0,'base':current,'desired':desired,'expected_merged':merged,'original_merged':original['merged']}));print('PATCH',sum(a!=c for a,c in zip(current,desired)))
