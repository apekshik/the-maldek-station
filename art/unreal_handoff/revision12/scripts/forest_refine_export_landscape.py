"""Export the current owned landscape into this pass's directory."""
from pathlib import Path
p=Path(__file__).resolve().parent/'export_landscape.py'
source=p.read_text().replace('base=Path(__file__).resolve().parents[1];','base=Path(__file__).resolve().parents[1]/\'forest_refine\';')
exec(compile(source,str(p),'exec'))
