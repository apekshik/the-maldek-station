import bpy,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Police_Cordon_Prototype.blend'))
s=bpy.context.scene;rows=[]
for f in [24,58,62,110,144]:
    s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get()
    for strand in ['', 'Lower_', 'Upper_']:
        points=[]
        for side in ['Left','Right']:
            ob=bpy.data.objects['Tape_'+strand+side];ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
            assert ob.data.uv_layers and len(ob.data.shape_keys.key_blocks)==145
            points.extend(tuple(v.co) for v in mesh.vertices)
            ev.to_mesh_clear()
        assert all(math.isfinite(v) for p in points for v in p)
        in_gap=sum(1 for x,y,z in points if abs(x)<.65 and z>.2)
        if f>=110:assert in_gap==0,(strand,f,in_gap)
        rows.append({'frame':f,'strand':strand or 'Middle','vertices_in_central_1_3m_gap':in_gap})
assert len([o for o in bpy.data.collections['04_Continuous_perimeter'].objects if o.name.startswith('Perimeter_span_')])==8
assert len(list((out/'exports').glob('*.fbx')))==36
(out/'verification.json').write_text(json.dumps({'passed':True,'crossing_gap_clear_after_release':True,'perimeter_spans':8,'export_files':36,'sampled_frames':rows},indent=2))
print('CORDON_VERIFIED')
