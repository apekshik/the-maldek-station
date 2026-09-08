"""Daylight visibility check of full terrain and the embedded station base."""
from pathlib import Path
requested=globals().get('JOB',{})
p=Path(__file__).resolve().parent/'forest_refine_capture.py'
JOB={'warmup':18,'shots':[
 ['down',[-18,7.15,5.8],[-21,27,-12]],
 ['foundation',[-34,14,5],[-15,-3,1.5]],
 ['overview',[-42,64,34],[-3,12,-8]],
 ['valley',[-18,7.15,5.8],[-18,160,-35]]
]}
if requested.get('overview_only'):JOB['shots']=[JOB['shots'][2]]
source=p.read_text().replace("out=b/'forest_refine'/JOB.get('stage','after')","out=b/'gorge'/'daylight'").replace('1800,1000','1440,900')
exec(compile(source,str(p),'exec'))
