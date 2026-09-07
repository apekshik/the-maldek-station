import json,time,sys
from pathlib import Path
b=Path(__file__).resolve().parents[1];stage=sys.argv[1] if len(sys.argv)>1 else 'full'
job={'id':'review-'+stage+'-'+str(time.time_ns()),'script':'capture_review.py','stage':stage}
if stage=='circulation':job['shots']=[['sideways_arrival',[-25,-22,9],[-17,-14,3]],['rear_cleanup',[23,-10,10],[13,-2,0]],['deck_borders',[8,15,13],[-3,1,4]],['bridge_junction',[18,11,8],[12,7,4]]]
(b/'request.json').write_text(json.dumps(job))
