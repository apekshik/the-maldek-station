"""Player views of the cliff, mountain composition, and embedded station base."""
from pathlib import Path
p=Path(__file__).resolve().parent/'forest_refine_capture.py'
JOB={'stage':'unused','warmup':12,'shots':[
 ['down',[-18,7.15,5.8],[-21,27,-12]],
 ['mountains',[-18,7.15,5.8],[-18,240,-10]],
 ['foundation',[-34,14,5],[-15,-3,1.5]]
]}
source=p.read_text().replace("out=b/'forest_refine'/JOB.get('stage','after')","out=b/'gorge'/'review'").replace('1800,1000','1440,900')
exec(compile(source,str(p),'exec'))
