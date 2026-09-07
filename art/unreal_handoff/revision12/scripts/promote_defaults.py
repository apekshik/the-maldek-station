"""Promote only after the saved level passes the declared pre-promotion gates."""
import json,re,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
required={'acceptance_circulation.json':'accepted','acceptance_architecture.json':'accepted','acceptance_infrastructure.json':'accepted',
 'foliage_persistence.json':'success','reference_validation.json':'success','behavior_validation.json':'success',
 'routes_continuous.json':'success','performance_comparison.json':'accepted','movement_performance_comparison.json':'accepted','hitch_review.json':'accepted','preservation_verification.json':'success',
 'package-explicit-build.json':'success','package-explicit-smoke.json':'success','package-explicit-visual.json':'accepted'}
evidence={}
for filename,key in required.items():
 p=b/filename;data=json.loads(p.read_text(encoding='utf-8-sig'));assert data.get(key) is True,('Gate not passed',filename,key)
 evidence[filename]=hashlib.sha256(p.read_bytes()).hexdigest()
p=repo/'game/Config/DefaultEngine.ini';text=p.read_text();old={}
new='/Game/MaldekRefinement/R12/Station_R12.Station_R12'
for key in ['EditorStartupMap','GameDefaultMap']:
 matches=re.findall(r'^'+key+r'=(.*)$',text,re.M);assert len(matches)==1
 old[key]=matches[0];text=re.sub(r'^'+key+r'=.*$',key+'='+new,text,flags=re.M)
p.write_text(text)
(b/'default_map_promotion.json').write_text(json.dumps({'promoted':True,'previous':old,'current':{k:new for k in old},'evidence_sha256':evidence,'game_mode':'Inherited BP_ForestGameMode from the level; project global game mode unchanged.','post_promotion_required':'Repackage without map override and validate actual default startup.'},indent=2))
print('Default maps promoted; default packaged startup remains a separate gate.')
