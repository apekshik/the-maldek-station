import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r'C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/police_tape/wrap_fit/SK_European_Aspen_01_D.fbx',use_anim=False)
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 print('materials',[m.name for m in ob.data.materials])
 ob.data.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in ob.data.vertices]
 for t in ob.data.loop_triangles:
  tri=[vs[i] for i in t.vertices]
  if min(v.z for v in tri)<1.4<max(v.z for v in tri):print('TRI',t.material_index,[tuple(v) for v in tri])
