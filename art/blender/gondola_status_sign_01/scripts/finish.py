"""Weld curve cap rings in the delivered sign geometry; source paths live in build.py."""
import bpy,bmesh,math
def finish():
 bpy.data.objects['NS01_Transformer_plate'].rotation_euler=(math.pi/2,0,math.pi)
 seen=set()
 for o in list(bpy.data.collections['NS01_Stationary_sign'].objects):
  if not o.name.startswith('NS01_Electrode_'):continue
  key=tuple(round(v,6) for v in o.location)
  if key in seen:bpy.data.objects.remove(o,do_unlink=True)
  else:seen.add(key)
 for o in list(bpy.data.collections['NS01_Stationary_sign'].objects):
  if o.type!='CURVE':continue
  sp=o.data.splines[0]
  pts=[tuple(p.co) for p in sp.points]
  if (sp.points[0].co-sp.points[-1].co).length<1e-6:
   o.data.splines.clear();sp=o.data.splines.new('POLY');sp.points.add(len(pts)-2)
   for p,v in zip(sp.points,pts[:-1]):p.co=v
   sp.use_cyclic_u=True;o.data.use_fill_caps=False
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT')
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'

if __name__=='__main__':
 finish();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
