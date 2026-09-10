"""Lower only native ground that would protrude through the new stair recess."""
import unreal,json,math,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent));from site_shape import height
b=json.loads((OUT/'before.json').read_text());o=b['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_Lodge_Migration'
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.Landscape))
paths=list(unreal.StationMigrationLibrary.get_landscape_heightmap_paths(land));assert paths and all(p.startswith('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration.') for p in paths)
cx=(o[0]+105812)/100;cy=(o[1]+138209)/100
bounds=[math.floor(cx+5),math.floor(cy-17),math.ceil(cx+10),math.ceil(cy-7)]
merged=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,-1));base=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,0));assert merged and base
desired=base.copy();width=bounds[2]-bounds[0]+1
for py in range(bounds[1],bounds[3]+1):
 y=(-138209+py*100-o[1])/100
 for px in range(bounds[0],bounds[2]+1):
  x=(o[0]-(-105812+px*100))/100;i=(py-bounds[1])*width+px-bounds[0]
  old=(23763+(merged[i]-32768)*100/128-o[2])/100
  target=min(old,height(3.48,x,y)-.65)
  if not (-9.6<x<-5.05 and -16.5<y<-7.2):continue
  raw=round(32768+(o[2]+target*100-23763)*128/100)
  desired[i]=max(0,min(65535,base[i]+raw-merged[i]))
report={'bounds':bounds,'base':base,'merged':merged,'desired':desired,'heightmap_paths':paths,'changed':sum(a!=b for a,b in zip(base,desired))}
(OUT/'native_ground_patch.json').write_text(json.dumps(report,indent=2))
result=unreal.StationMigrationLibrary.apply_r12_landscape_patch(land,*bounds,0,base,desired);assert result.startswith('OK'),result
assert list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*bounds,0))==desired
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
RESULT={'result':result,'readback':True,'ownership_verified':True}
(OUT/'native_ground_applied.json').write_text(json.dumps(RESULT,indent=2))
