import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('tune_r07_ambient.py')))
runpy.run_path(str(Path(__file__).with_name('test_r07.py')))
