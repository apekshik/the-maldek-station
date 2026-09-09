"""Approved neon sign only: cabinet and four independent circuits, origin at foot."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/gondola_sign';out.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(__file__).parent));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/gondola_status_sign_01/Maldek_Gondola_Status_Sign.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));s=bpy.context.scene;s.frame_set(145);bpy.context.view_layer.update()
h.collision_kind=lambda o:None
handoff=h.Handoff(s,bpy.context.evaluated_depsgraph_get(),'fbx');pivot=bpy.data.objects['NS01_Mount_origin'].matrix_world.translation
objects=list(bpy.data.collections['NS01_Stationary_sign'].objects)
neon=[o for o in objects if o.name.startswith(('NS01_Neon_','NS01_Pilot_'))]
for word in ['BOARD','ARRIVING','DEPART','AWAY']:
 obs=[o for o in neon if any(m and m.name=='NS01_Circuit_'+word for m in o.data.materials)]
 handoff.chunk('SM_Status_'+word,obs,pivot=pivot,role='thin')
def box(c,d):return {'min':[pivot[i]+c[i]-d[i]/2 for i in range(3)],'max':[pivot[i]+c[i]+d[i]/2 for i in range(3)],'kind':'authored','source':'sign collision'}
boxes=[box((0,.155,.765),(.12,.12,1.53)),box((0,.06,2.18),(1.55,.32,1.44))]
handoff.chunk('SM_Status_Cabinet',[o for o in objects if o not in neon],pivot=pivot,extra_boxes=boxes,role='thin')
(out/'manifest.json').write_text(json.dumps({'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'materials':handoff.materials,'chunks':handoff.chunks,'axis':'Imported (x,-y,z); yaw 180 produces (-x,y,z)','source_mount_relative_to_cabin_m':list(pivot),'review_context_exported':False},indent=2))
