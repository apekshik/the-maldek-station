"""Check reachable package references, material compilation and inherited player/controller BPs."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
registry=unreal.AssetRegistryHelpers.get_asset_registry();options=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
pending=['/Game/MaldekRefinement/R12/Station_R12'];seen=set();missing=[]
while pending:
 p=pending.pop()
 if p in seen or p.startswith('/Script/'):continue
 seen.add(p)
 deps=registry.get_dependencies(p,options) or []
 for dep in deps:
  q=str(dep)
  if q.startswith('/Script/'):continue
  if not registry.get_assets_by_package_name(q):missing.append({'referencer':p,'missing':q})
  elif q not in seen:pending.append(q)
blueprints=[]
for p in ['/Game/MaldekRefinement/ForestTest/BP_ForestWalker','/Game/BP_GondolaSystem']:
 bp=lib.load_asset(p);assert bp
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);blueprints.append({'asset':p,'up_to_date':unreal.StationMigrationLibrary.is_blueprint_up_to_date(bp)})
materials=[]
for p in lib.list_assets('/Game/MaldekRefinement/R12/Materials',True,False):
 a=lib.load_asset(p)
 if isinstance(a,unreal.MaterialInterface):materials.append(a)
errors=list(unreal.StationMigrationLibrary.validate_material_shaders(materials))
known='/Game/Megaplant_Library/Tree_European_Beech/Instances/Beech_Branch'
new_missing=[r for r in missing if not r['missing'].startswith(known)]
report={'success':not new_missing and not errors and all(x['up_to_date'] for x in blueprints),'reachable_packages':len(seen),'missing_references':missing,'new_missing_references':new_missing,'preexisting_authoring_reference_prefix':known,'blueprints':blueprints,'material_shader_errors':errors,'material_count':len(materials),'shared_assets_saved':False}
(b/'reference_validation.json').write_text(json.dumps(report,indent=2));RESULT=report
