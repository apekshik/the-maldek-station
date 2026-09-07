"""Window reveal repair retaining the accepted door and quarters beam fixes."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('trim2_recess_cores.py')),init_globals={'WINDOW_REPAIR':True})
