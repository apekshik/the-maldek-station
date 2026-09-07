from pathlib import Path
src=Path(__file__).resolve().parents[2]/'visual_fidelity_03/scripts/verify_revision.py'
code=src.read_text().replace('middle=coverage(6.4);outer=coverage(8.56)','middle=coverage(8.1);outer=coverage(11.3)').replace('[(7.8,y)','[(9.6,y)').replace('(x,7.2)','(x,9.0)')
exec(compile(code,__file__,'exec'))
checks=[]
for x,y in [(14,2),(16,2),(18,2),(14,10),(16,12),(16,15),(18.5,15)]:
 r=hit((x,y,.15),(0,0,-1),.2);add('Wide connector floor',r[0],x=x,y=y)
 for z in [.5,1.7]:add('Connector headroom',not hit((x,y,z),(0,0,1),.4)[0],x=x,y=y)
for y in [1,2,3,10,11,12]:
 for z in [.4,1,1.7]:add('Main side entrances',not hit((13,y,z),(1,0,0),.8)[0],y=y,z=z)
# Side grating and plate bands match the same outward order as the frontage.
for x,kind in [(6.65,'grating'),(9.55,'solid'),(12.25,'grating')]:
 hits=0
 for i in range(19):
  for j in range(11):hits+=hit((x+i*.021,3.43+j*.019,.035),(0,0,-1),.065)[0]
 fraction=hits/209;add('Side band '+kind,fraction>.9 if kind=='solid' else fraction<.65,coverage=fraction)
report={'count':len(checks),'passed':all(c['passed'] for c in checks),'failures':[c for c in checks if not c['passed']],'bands_m':[1.8,3.6,1.95],'total_depth_m':7.35,'limits':'Sampled Blender geometry, not an engine capsule test.'}
(out/'wide_platform_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['passed']
