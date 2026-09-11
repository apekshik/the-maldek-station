import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r'C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/police_tape/wrap_fit/axis_probe.fbx',use_anim=False)
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];print('BOUNDS',[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)])
