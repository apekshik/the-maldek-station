import runpy
from pathlib import Path
p=Path(__file__).resolve().parent
runpy.run_path(str(p/'setup_r09_character.py'))
runpy.run_path(str(p/'playtest_r09.py'))
