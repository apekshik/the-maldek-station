import runpy
from pathlib import Path
scripts=Path(__file__).resolve().parent
runpy.run_path(str(scripts/'place_r08_wall_lights.py'))
runpy.run_path(str(scripts/'verify_r08.py'))
runpy.run_path(str(scripts/'render_r08.py'))
