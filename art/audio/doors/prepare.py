"""Rebuild the door bank from downloaded recordings; the old synthesized bank is retired."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent/'recorded/prepare_recorded.py'))
