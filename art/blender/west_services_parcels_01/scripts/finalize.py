from pathlib import Path
import hashlib,json,struct
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={n:json.loads((P/n).read_text()) for n in ['verification.json','fitted_verification.json','surface_verification.json','deposit_demonstration.json']}
assert all(reports[n]['passed'] for n in ['verification.json','fitted_verification.json','surface_verification.json'])
assert reports['deposit_demonstration.json']['shelving_unchanged']
assert (P/'verification.json').stat().st_mtime >= (P/'Maldek_Parcels_Office.blend').stat().st_mtime
assert (P/'fitted_verification.json').stat().st_mtime >= (P/'Maldek_Parcels_Fitted_Review.blend').stat().st_mtime
images=[]
for name in ['01_porch_closed','02_door_open','03_rear_shelves','04_counter_reverse','05_tag_station','06_secure_closed','07_secure_open','08_window_closed','09_door_inside_closed','10_threshold','11_deposit_removed','12_handling_plan','13_trolley_turned','14_trolley_porch_turn']:
 p=P/'previews'/f'{name}.png';data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);assert w>=1000 and h>=750;images.append({'file':str(p.relative_to(P)),'sha256':sha(p),'size':[w,h]})
a=json.loads((P/'assembly.json').read_text());source=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend';assert sha(source)==a['source_sha256']
lo,hi=a['operator_aisle_local'];lo[2]=.021;hi[2]=1.8
def intersect(b):return all(b[1][i]>lo[i]+.0001 and b[0][i]<hi[i]-.0001 for i in range(3))
aisle_hits=[n for n,v in reports['verification.json']['inventory'].items() if intersect(v['bounds'])]
aisle_hits += [n for n,v in reports['verification.json']['sweeps'].items() if intersect(v['bounds'])]
assert not aisle_hits,aisle_hits
(P/'operator_aisle_verification.json').write_text(json.dumps({'passed':True,'region':[lo,hi],'width_m':hi[0]-lo[0],'method':'Conservative closed-mesh bounds plus every recorded mechanism swept AABB. Includes extended clerk drawer and handle.','hits':aisle_hits},indent=2))
out={'asset_blend':'Maldek_Parcels_Office.blend','asset_sha256':sha(P/'Maldek_Parcels_Office.blend'),'fitted_review_blend':'Maldek_Parcels_Fitted_Review.blend','fitted_sha256':sha(P/'Maldek_Parcels_Fitted_Review.blend'),'immutable_master_sha256':sha(source),'verification_passed':True,'geometry_meshes':reports['verification.json']['meshes'],'images':images,'integration_limitations':['No Unreal/map/runtime edits or imports','Engine material bakes, UV atlas/lightmap preparation, LODs, export basis verification and collision/traversal remain','Shared shell polish and final assembly belong to a later task']}
(P/'delivery.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
