import unreal,json
from pathlib import Path
lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/R09'
bp=lib.load_asset(root+'/BP_StationWalker') or lib.duplicate_asset('/Game/Variant_Horror/Blueprints/BP_HorrorCharacter',root+'/BP_StationWalker')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);f=unreal.SubobjectDataBlueprintFunctionLibrary
r={'params_doc':unreal.AddNewSubobjectParams.__doc__,'handles':[]}
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 d=f.get_data(h);o=f.get_object(d);r['handles'].append({'name':o.get_name(),'class':o.get_class().get_name(),'path':o.get_path_name()})
(Path(__file__).resolve().parents[1]/'revision09/character_setup_audit.json').write_text(json.dumps(r,indent=2))
