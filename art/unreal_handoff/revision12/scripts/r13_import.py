import runpy
from pathlib import Path
RESULT=runpy.run_path(str(Path(__file__).resolve().parents[2]/'revision13/scripts/import_service.py'),init_globals={'JOB':JOB})['RESULT']
