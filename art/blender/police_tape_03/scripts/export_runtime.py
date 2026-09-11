import bpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'exports'
bpy.ops.wm.read_factory_settings(use_empty=True)
v=[];f=[]
for i in range(9):v.extend([(i/8,0,-.0381),(i/8,0,.0381)])
for i in range(8):a=i*2;f.append((a,a+2,a+3,a+1))
m=bpy.data.meshes.new('Ribbon');m.from_pydata(v,[],f);m.update();uv=m.uv_layers.new()
for p in m.polygons:
 for li in p.loop_indices:
  i=m.loops[li].vertex_index;uv.data[li].uv=((i//2)/8,i%2)
o=bpy.data.objects.new('SM_Tape_RuntimeSegment',m);bpy.context.scene.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Tape_RuntimeSegment.fbx'),use_selection=True,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
# Single trunk wrap; scales independently to surveyed trunk radii.
bpy.ops.wm.open_mainfile(filepath=str(out.parent/'Maldek_Crisscross_Cordon.blend'))
src=bpy.data.objects['Wrap_Rising_Left'];src.location.x=1.8;src.location.z=-.97
bpy.ops.object.select_all(action='DESELECT');src.select_set(True);bpy.context.view_layer.objects.active=src
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Tape_TrunkWrap.fbx'),use_selection=True,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
