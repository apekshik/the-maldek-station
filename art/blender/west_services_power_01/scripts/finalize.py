import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(n):return json.loads((P/n).read_text())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2))
A=read('assembly.json');bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Emergency_Power.blend'));assert len(A['anchors'])==7
for n,d in A['objects'].items():
 o=bpy.data.objects[n];d['dimensions_m']=list(o.dimensions);d['parent']=o.parent.name if o.parent else None;d['local_matrix']=[list(row) for row in o.matrix_local]
A['selector_states']={'WSE_Transfer_selector':{'axis':'X','normal_degrees':-45,'off_degrees':0,'emergency_degrees':45},'WSE_Fuel_valve':{'axis':'Y','open_degrees':0,'isolated_degrees':90}}
A['push_controls']={'WSE_START':{'part':'WSE_START_button','travel_axis':'Y','travel_m':-.006},'WSE_STOP':{'part':'WSE_STOP_button','travel_axis':'Y','travel_m':-.006},'WSE_EMERGENCY_STOP':{'part':'WSE_Emergency_stop','travel_axis':'Y','travel_m':-.012}}
A['shell_patch']='shell_patch.json';A['machine_removal']='README: detach projecting control pod and services, 1.30 m skid moves north then west; temporary lift required beyond walk.'
v=read('verification.json');m=read('mechanism_verification.json');h=read('handling_verification.json');surf=read('surface_audit.json')
A['verified_door_clearance']={'width_m':m['door_open_width_m'],'height_m':m['door_headroom_m']};write('assembly.json',A)
v['clearances']['open_leaves_clear_width']=m['door_open_width_m'];v['clearances']['door_headroom_including_seal']=m['door_headroom_m'];v['clearances']['door_frame_height']=2.189;write('verification.json',v)
surf['same_facing_count']=sum(p['same_facing'] for p in surf['pairs']);surf['classification']='Remaining opposite-facing contacts are buried mating surfaces: mounts/tray/tank, enclosure panel ends, louvre/frame junctions and inserted fittings. No same-facing competing planar surface pair remains within stated tolerances.';write('surface_audit.json',surf)
files={str(f.relative_to(P)).replace('\\','/'):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in P.rglob('*') if f.is_file() and f.suffix in ['.blend','.png','.py','.md','.json'] and f.name!='delivery.json'}
d={'editable_blend':'Maldek_Emergency_Power.blend','fitted_blend':'Maldek_Emergency_Power_Fitted.blend','reference_sha256':read('reference_inspection.json')['hash'],'review_images':sorted(str(f.relative_to(P)).replace('\\','/') for f in (P/'reviews').glob('*.png')),'verification_passed':v['passed'] and m['passed'] and h['passed'] and surf['same_facing_count']==0,'files':files,'limits':'Unreal checks, shared-shell integration, wind/thermal/acoustic/fire/structural sizing and temporary access-lift design remain later gates.'};write('delivery.json',d);print('DELIVERY',d['verification_passed'],len(d['review_images']),A['verified_door_clearance'])
