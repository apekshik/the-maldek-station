import runpy
from pathlib import Path
p=Path(__file__).parent
runpy.run_path(str(p/'gondola_mechanism_frame_refresh.py'))
runpy.run_path(str(p/'gondola_mechanism_audio.py'))
RESULT=runpy.run_path(str(p/'gondola_mechanism_runtime.py'))['RESULT']
