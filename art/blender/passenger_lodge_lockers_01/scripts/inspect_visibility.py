import bpy,json
bpy.ops.wm.open_mainfile(filepath='C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend');s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
out=[]
def walk(l,depth=0):
 out.append((depth,l.name,l.exclude,l.hide_viewport,l.collection.hide_render))
 for c in l.children:walk(c,depth+1)
walk(bpy.context.view_layer.layer_collection)
print('LAYERS',json.dumps(out))
o=bpy.data.objects['Bench_back.001'];print('BENCH',o.hide_render,o.hide_get(),o.visible_get(),[c.name for c in o.users_collection])
