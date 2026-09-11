import runpy
from pathlib import Path
P=Path(__file__).parent
RESULT={n:runpy.run_path(str(P/(n+'.py'))).get('RESULT') for n in ['check_routes','audit_foliage']}
