"""Room sightline and red edge marker review in the actual player view."""
from pathlib import Path
requested=globals().get('JOB',{});p=Path(__file__).resolve().parent/'forest_refine_capture.py'
JOB={'stage':requested.get('stage','before'),'warmup':15,'shots':[
 ['quarters',[-4.5,.65,8.6],[0,8.8,5.4]],
 ['platform',[-20,3,4.95],[-5,9,4.8]],
 ['bridge_approach',[10,7,4.95],[19,36,4.9]],
 ['bridge_end',[18,29,4.95],[19,37,4.9]]
]}
if requested.get('shots'):JOB['shots']=[s for s in JOB['shots'] if s[0] in requested['shots']]
source=p.read_text().replace("out=b/'forest_refine'/JOB.get('stage','after')","out=b/'platform_refine'/JOB['stage']").replace('1800,1000','1440,900')
exec(compile(source,str(p),'exec'))
