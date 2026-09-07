import bpy
s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=720
s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1
def arrange():
    a=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
    with bpy.context.temp_override(area=a):bpy.ops.maldek_h3.compare()
    def save():
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        print('COMPARISON_READY',flush=True)
    bpy.app.timers.register(save,first_interval=3)
bpy.app.timers.register(arrange,first_interval=3)
