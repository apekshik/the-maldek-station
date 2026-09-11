import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Police_Tape_Prototype.blend'))
s=bpy.context.scene
rows=[]
for f in [1,24,58,59,72,96,144]:
    s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();ends=[]
    for name,edge in [('Tape_Left',-2),('Tape_Right',1)]:
        ob=bpy.data.objects[name];mesh=ob.evaluated_get(deps).to_mesh()
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        # Shape-key vertices are followed by the solidify back surface.
        vi=(len(ob.data.vertices)-2) if edge==-2 else 1
        ends.append(Vector(mesh.vertices[vi].co))
        ob.evaluated_get(deps).to_mesh_clear()
    rows.append({'frame':f,'seam_gap_m':(ends[0]-ends[1]).length})
assert rows[0]['seam_gap_m']<.01
assert rows[-1]['seam_gap_m']>1
assert bpy.data.images['T_PoliceTape_BaseColor.png'].packed_file
assert len(bpy.data.objects['Tape_Left'].data.shape_keys.key_blocks)==145
source_bounds={}
s.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
for name in ['Tape_Left','Tape_Right','Wrap_Left','Wrap_Right','Loose_tail_Left','Loose_tail_Right']:
    mesh=bpy.data.objects[name].evaluated_get(deps).to_mesh()
    source_bounds[name]=[[min(v.co[k] for v in mesh.vertices) for k in range(3)],[max(v.co[k] for v in mesh.vertices) for k in range(3)]]
    bpy.data.objects[name].evaluated_get(deps).to_mesh_clear()
exports=[]
for name,bounds in source_bounds.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(out/'exports'/f'SM_{name}.fbx'))
    ob=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    coords=[ob.matrix_world@v.co for v in ob.data.vertices]
    actual=[[min(v[k] for v in coords) for k in range(3)],[max(v[k] for v in coords) for k in range(3)]]
    error=max(abs(actual[a][b]-bounds[a][b]) for a in range(2) for b in range(3))
    assert error<.0001,(name,error)
    assert ob.data.uv_layers
    exports.append({'mesh':name,'roundtrip_bounds_error_m':error,'uvs_present':True})
(out/'verification.json').write_text(json.dumps({'passed':True,'packed_lettering':True,'animation_frames':144,'seam_samples':rows,'fbx_roundtrip':exports},indent=2))
print('TAPE_VERIFICATION_PASSED')
