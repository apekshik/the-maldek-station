import runpy
from pathlib import Path
p=Path(__file__).parent
runpy.run_path(str(p/'gondola_mechanism_rope_material.py'))
RESULT=runpy.run_path(str(p/'gondola_mechanism_motion_capture.py'))['RESULT']
