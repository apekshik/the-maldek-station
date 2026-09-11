import runpy
from pathlib import Path
RESULT=runpy.run_path(str(Path(__file__).resolve().parents[2]/'west_services_01/scripts/session.py')).get('RESULT')
