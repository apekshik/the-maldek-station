import runpy
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'revision13/scripts'
RESULT=runpy.run_path(str(p/'environment.py'),init_globals={'JOB':JOB})['RESULT']
runpy.run_path(str(p/'export_landscape.py'))
