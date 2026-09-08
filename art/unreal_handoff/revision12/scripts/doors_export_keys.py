"""Export the approved key study with independent lock pivots and fitted leaf variants."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/doors/key_lock';out.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(__file__).parent));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/door_study_04/Maldek_Keyed_Door.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));s=bpy.context.scene;s.frame_set(30);bpy.context.view_layer.update()
handoff=h.Handoff(s,bpy.context.evaluated_depsgraph_get(),'fbx')
for name,objects,pivot in [('Housing',list(bpy.data.collections['07_Key_cylinder_housings'].objects),(1.15,0,1)),('Plug',list(bpy.data.objects['D04_PLUG_FRONT'].children),(1.15,-.046,1)),('Key',list(bpy.data.collections['09_Cut_service_key'].objects),(1.15,-.046,1))]:
 handoff.chunk('SM_KeyLock_'+name,objects,pivot=pivot,role='thin')
leaf=bpy.data.collections['01_Moving_leaf'];objects=[o for o in leaf.objects if o.name!='Vision_glass']
for name,code,title in [('Control','C / 01','CONTROL'),('Hall','H / 01','WAITING HALL'),('Generator','G / 01','GENERATOR'),('Workshop','W / 01','WORKSHOP')]:
 bpy.data.objects['Door_ID'].data.body=code;bpy.data.objects['Door_ID_sub'].data.body=title;bpy.context.view_layer.update();handoff.deps=bpy.context.evaluated_depsgraph_get();handoff.chunk('SM_KeyLock_'+name+'Leaf',objects,pivot=(.004,-.035,0),role='thin')
# Preserve the proven inward hinge construction, without changing jambs or collision.
for o in objects:
 if o.type not in ['MESH','FONT']:continue
 p=o.matrix_world.translation.copy()
 if o.name.startswith('Moving_hinge') or (abs(p.x-.056)<.002 and p.y<-.03):m=o.matrix_world.copy();m.translation.y=-p.y;o.matrix_world=m
bpy.data.objects['Pull_instruction'].data.body='PUSH TO OPEN'
for name,code,title in [('Quarters','Q / 01','QUARTERS'),('GeneratorInward','G / 01','GENERATOR')]:
 bpy.data.objects['Door_ID'].data.body=code;bpy.data.objects['Door_ID_sub'].data.body=title;bpy.context.view_layer.update();handoff.deps=bpy.context.evaluated_depsgraph_get();handoff.chunk('SM_KeyLock_'+name+'Leaf',objects,pivot=(.004,.035,0),role='thin')
(out/'manifest.json').write_text(json.dumps({'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'materials':handoff.materials,'chunks':handoff.chunks,'units':'metres, FBX converted once to centimetres','key_seated_pivot_cm':[0,4.6,0],'insertion_travel_cm':8},indent=2))
