import runpy
from pathlib import Path
b=Path(__file__).resolve().parent
for script,args in [('validate_materials.py',{}),('audit_stage.py',{'stage':JOB['stage']})]:
 runpy.run_path(str(b/script),init_globals={'JOB':args})
RESULT={'success':True,'stage':JOB['stage'],'shader_validation':'shader_validation.json','audit':'audit_'+JOB['stage'].lower()+'.json'}
