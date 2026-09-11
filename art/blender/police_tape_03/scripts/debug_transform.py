import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r'C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/police_tape/wrap_fit/SK_European_Beech_01_B.fbx',use_anim=False)
for ob in bpy.context.scene.objects:
 print(ob.name,ob.type,'MAT',ob.matrix_world,'MOD',[(m.name,m.type) for m in ob.modifiers])
 if ob.type=='ARMATURE':print('ROOT',ob.data.bones[0].matrix_local)

for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];print('EVAL',[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)])
  raw=[ob.matrix_world@v.co for v in ob.data.vertices];print('DIFF',max((a-b).length for a,b in zip(raw,vs)))

for ob in bpy.context.scene.objects:
 if ob.type=='ARMATURE':
  print('BONES',[(b.name,tuple(ob.matrix_world@b.head_local)) for b in list(ob.data.bones)[:8]])
