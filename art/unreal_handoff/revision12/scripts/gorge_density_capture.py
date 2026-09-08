"""Repeatable player-height review from occupied station viewpoints."""
from pathlib import Path
requested=globals().get('JOB',{});p=Path(__file__).resolve().parent/'forest_refine_capture.py'
JOB={'warmup':15,'stage':requested.get('stage','density_before'),'shots':[
 ['gondola',[0,10.3,4.95],[0,52,-20]],
 ['ground_floor',[-5.9,6.8,4.95],[-16,40,-16]],
 ['basement',[3.2,4.1,1.0],[19,30,-13]],
 ['west_side',[-23,5,4.95],[-47,24,-8]],
 ['east_side',[6.8,6.4,4.95],[38,22,-9]],
 ['back_stairs',[-18,-10,4.95],[-25,-16,2]],
 ['stairs_east',[7,-.3,1],[7,7,3]]
 ,['ground_down',[-5.9,6.8,4.95],[-7,32,-45]]
 ,['basement_front',[3.2,4.4,1],[3.2,28,-13]]
 ,['basement_edge',[3.2,10.5,.95],[5,30,-15]]
]}
if requested.get('shots'):JOB['shots']=[s for s in JOB['shots'] if s[0] in requested['shots']]
source=p.read_text().replace("out=b/'forest_refine'/JOB.get('stage','after')","out=b/'gorge'/'density'/JOB['stage']").replace('1800,1000','1440,900')
exec(compile(source,str(p),'exec'))
