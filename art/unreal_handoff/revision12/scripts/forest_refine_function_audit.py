import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];p='/Game/MWLandscapeAutoMaterial/Materials/MASTER/Func/MF_MWAM_SnowMask';f=unreal.load_asset(p)
rows=[]
for n in unreal.ObjectIterator(unreal.MaterialExpression):
 if n.get_outer()==f:
  row={'name':n.get_name(),'class':n.get_class().get_name()}
  if isinstance(n,unreal.MaterialExpressionScalarParameter):row['parameter']=str(n.get_editor_property('parameter_name'))
  rows.append(row)
RESULT={'nodes':rows};(b/'forest_refine'/'function_audit.json').write_text(json.dumps(RESULT,indent=2))
