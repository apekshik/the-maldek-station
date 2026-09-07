"""Offline local underlay clearance; preserve every pixel outside the explicit station mask."""
from pathlib import Path
from PIL import Image
import json,bisect,hashlib,math
base=Path(__file__).resolve().parents[1];g=json.loads((base/'terrain_grid.json').read_text());origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
own=json.loads((base/'landscape_ownership.json').read_text());assert own['exported'] and own['components']
vs=g['vertices'];xs=sorted(set(p[0] for p in vs));ys=sorted(set(p[1] for p in vs));z={(p[0],p[1]):p[2] for p in vs}
previous=json.loads((base.parent/'revision12/terrain_grid.json').read_text());forest={(p[0],p[1]):p[2] for p in previous['vertices']}
def previous_height(x,y):
 i=max(0,min(len(xs)-2,bisect.bisect_right(xs,x)-1));j=max(0,min(len(ys)-2,bisect.bisect_right(ys,y)-1));x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];u=(x-x0)/(x1-x0);v=(y-y0)/(y1-y0)
 return (1-v)*((1-u)*forest[x0,y0]+u*forest[x1,y0])+v*((1-u)*forest[x0,y1]+u*forest[x1,y1])

def height(x,y):
 i=max(0,min(len(xs)-2,bisect.bisect_right(xs,x)-1));j=max(0,min(len(ys)-2,bisect.bisect_right(ys,y)-1));x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];u=(x-x0)/(x1-x0);v=(y-y0)/(y1-y0)
 return (1-v)*((1-u)*z[x0,y0]+u*z[x1,y0])+v*((1-u)*z[x0,y1]+u*z[x1,y1])
before=Image.open(base/'landscape_before.png').convert('RGBA');after=before.copy();pix=after.load();changes=[];mask=[[17,44],[-28,-7]]
assert before.getextrema()[0][1]>0 and before.getextrema()[1][1]>0,'Blank Landscape export is invalid; do not apply it'
minimum_existing_clearance=float('inf');sampled_pixels=0
for py in range(4033):
 y=((-138209+py*100)-origin[1])/100
 if not mask[1][0]<=y<=mask[1][1]:continue
 for px in range(4033):
  x=(origin[0]-(-105812+px*100))/100
  if not mask[0][0]<=x<=mask[0][1]:continue
  terrain=height(x,y)
  # The rectangle is an envelope, not permission to alter unchanged canyon data.
  # Only pixels touched by the actual VF07 terrain delta belong to the change mask.
  if abs(terrain-previous_height(x,y))<.001:continue
  r,green,b,a=pix[px,py];old=r*256+green
  underlay=(23763+(old-32768)*100/128-origin[2])/100
  minimum_existing_clearance=min(minimum_existing_clearance,terrain-underlay);sampled_pixels+=1
  desired=max(0,min(65535,round(32768+(origin[2]+100*(terrain-.6)-23763)*128/100)))
  if desired<old:
   pix[px,py]=(desired//256,desired%256,b,a);changes.append([px,py,old,desired,x,y])
after.save(base/'landscape_r13.png')
report={'success':minimum_existing_clearance>=.6 or bool(changes),'mask_envelope':mask,'active_mask':'abs(combined R12 height - latest forest height) >= 0.001 m','changed_pixels':len(changes),'outside_mask_changes':0,'required_underlay_clearance_m':.6,'measured_minimum_existing_clearance_m':minimum_existing_clearance,'sampled_pixels':sampled_pixels,'source_sha256':hashlib.sha256((base/'landscape_before.png').read_bytes()).hexdigest(),'result_sha256':hashlib.sha256((base/'landscape_r13.png').read_bytes()).hexdigest(),'pixels':changes}
(base/'landscape_delta.json').write_text(json.dumps(report,indent=2));print('LOCAL_LANDSCAPE_CUT',len(changes))
