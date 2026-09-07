"""Compare authoritative foliage data after reopening, including all untouched instances."""
import unreal,json,re
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
inventory=json.loads((b/'foliage_instance_inventory.json').read_text());moves={r['key']:r for r in json.loads((b/'foliage_relocations.json').read_text())['moves']}
a=next(a for a in aa.get_all_level_actors() if a.get_path_name()==inventory['actor']);actual=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a)
assert len(actual)==len(inventory['instances'])
def clean(s):return re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',str(s))
for row in inventory['instances']:
 t=actual[row['key']];expected=moves.get(row['key'],{}).get('new_world',row['world'])
 assert (t.translation-unreal.Vector(*expected)).length()<.1,row['key']
 assert clean(t.rotation)==clean(row['rotation']),row['key']
 assert clean(t.scale3d)==clean(row['scale']),row['key']
report={'success':True,'instances':len(actual),'relocated':len(moves),'untouched':len(actual)-len(moves),'rotations_and_scales_preserved':True,'checked_after_reopen':JOB.get('after_reopen',False)}
(b/'foliage_persistence.json').write_text(json.dumps(report,indent=2));RESULT=report
