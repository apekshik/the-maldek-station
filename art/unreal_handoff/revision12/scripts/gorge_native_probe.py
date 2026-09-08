"""Read just the candidate rectangle from the current terrain and its base layer."""
import unreal,json,math,sys
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import height,weight
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.Landscape))
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
cx=(o[0]+105812)/100;cy=(o[1]+138209)/100
bounds=[math.floor(cx-111),math.floor(cy-15),math.ceil(cx+96),math.ceil(cy+170)]
merged=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,-1))
base=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,0));assert merged and base
width=bounds[2]-bounds[0]+1;desired=base.copy();expected_merged=merged.copy();count=0
grid={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 if not all(k in grid for k in [(i,j),(i+1,j),(i,j+1),(i+1,j+1)]):return None
 return (1-v)*((1-u)*grid[i,j]+u*grid[i+1,j])+v*((1-u)*grid[i,j+1]+u*grid[i+1,j+1])
for py in range(bounds[1],bounds[3]+1):
 y=(-138209+py*100-o[1])/100
 for px in range(bounds[0],bounds[2]+1):
  x=(o[0]-(-105812+px*100))/100
  if not weight(x,y):continue
  i=(py-bounds[1])*width+px-bounds[0];old=merged[i]
  z=(23763+(old-32768)*100/128-o[2])/100;target=height(z,x,y);surface=ground(x,y)
  if surface is not None:target=min(target,surface-.65)
  new=max(0,min(65535,round(32768+(o[2]+100*target-23763)*128/100)))
  desired[i]=max(0,min(65535,base[i]+new-old));expected_merged[i]=new;count+=new!=old
report={'bounds':bounds,'layer':0,'merged':merged,'base':base,'desired':desired,'expected_merged':expected_merged,'source':'native CPU height data','changed':count,'base_equals_merged':base==merged}
(out/'native_probe.json').write_text(json.dumps(report))
RESULT={'bounds':bounds,'source':report['source'],'changed':count,'base_equals_merged':base==merged}
