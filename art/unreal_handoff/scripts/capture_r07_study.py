from pathlib import Path
import runpy
scripts=Path(__file__).resolve().parent
runpy.run_path(str(scripts/'place_r07_lighting_study.py'))
runpy.run_path(str(scripts/'reload_r07.py'))
runpy.run_path(str(scripts/'render_r07.py'))
