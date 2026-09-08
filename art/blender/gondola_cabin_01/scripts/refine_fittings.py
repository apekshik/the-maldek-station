"""Finish retained entry glazing and provide warm, separate studio inspection lights."""
import bpy,bmesh
from pathlib import Path
def refine():
 s=bpy.context.scene;s.frame_set(60);bpy.context.view_layer.update()
 # Closed leaves overlap the stationary head/jamb brushes without narrowing the opening.
 for o in s.objects:
  if o.name.startswith('GC_Leaf_stile'):o.location.z=1.068;o.dimensions.z=2.096
  elif o.name.startswith('GC_Leaf_crossrail') and o.location.z>2:o.location.z=2.055;o.dimensions.z=.120
  elif o.name.startswith('GC_Jamb_seal'):
   o.location.x=.620 if o.location.x>0 else -.620;o.location.y=-3.091;o.dimensions=(.040,.066,2.10)
  elif o.name=='GC_Top_seal':o.location.y=-3.091;o.dimensions=(1.20,.066,.030)
  elif o.name.startswith('GC_Replaceable_sweep'):o.location.z=.011;o.dimensions.z=.020
 # The window cores are open: service boxes need supports connected to the frames.
 for sign,z in [(1,1.28),(-1,1.38)]:
  name='GC_Service_mount_beam_'+str(sign)
  if not bpy.data.objects.get(name):
   bpy.ops.mesh.primitive_cube_add(size=1,location=(sign*1.10,-2.958,z));o=bpy.context.object;o.name=name;o.dimensions=(.84,.036,.075);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   for c in list(o.users_collection):c.objects.unlink(o)
   bpy.data.collections['04_Cabin_interior_details'].objects.link(o);o.data.materials.append(bpy.data.materials['GC01_Graphite']);mod=o.modifiers.new('Soft fabricated edges','BEVEL');mod.width=.003;mod.segments=3
   world=o.matrix_world.copy();o.parent=bpy.data.objects['GC_CABIN_APPROACH_ROOT'];o.matrix_world=world
 # Blender's capped curve conversion leaves coincident cap rings unwelded.
 for o in list(s.objects):
  if o.type=='CURVE' and o.name.startswith(('GC_Protected_wiring','GC_Coat_hook')):
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(o.data);bm.free();o.data.update()
 for name,sign in [('Gondola_South_Pier',-1),('Gondola_South_End',1)]:
  o=bpy.data.objects[name]
  if not o.get('GC01_entry_glazing_cut'):
   bpy.ops.mesh.primitive_cube_add(size=1,location=(sign*1.10,-3.02,1.49));tool=bpy.context.object;tool.dimensions=(.72,.60,1.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('GC01 through-opening behind entry glazing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True);o['GC01_entry_glazing_cut']=True
 m=bpy.data.materials.get('GC01_Lamp_diffuser') or bpy.data.materials.new('GC01_Lamp_diffuser');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.75,.68,.48,1);p.inputs['Roughness'].default_value=.5;p.inputs['Emission Color'].default_value=(1,.68,.35,1);p.inputs['Emission Strength'].default_value=.6
 for o in s.objects:
  if o.name.startswith('Cabin_ceiling_light'):o.data.materials.clear();o.data.materials.append(m)
 for i,y in enumerate([-1.65,1.55]):
  name=f'GC01_Review_interior_fill_{i}'
  if bpy.data.objects.get(name):continue
  data=bpy.data.lights.new(name,'AREA');data.energy=18;data.color=(1,.68,.38);data.shape='RECTANGLE';data.size=.76;data.size_y=.16;o=bpy.data.objects.new(name,data);bpy.data.collections['90_Review_studio'].objects.link(o);o.parent=bpy.data.objects['GC_CABIN_APPROACH_ROOT'];o.location=(0,y,2.225)
if __name__=='__main__':
 out=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Gondola_Cabin.blend'));refine();s=bpy.context.scene
 for name,cam,f in [('01_Closed','01_Cabin_exterior',60),('02_Open','01_Cabin_exterior',180),('03_Door_detail','02_Door_detail',60),('04_Interior','03_Interior',180),('05_Track','04_Track_detail',112),('06_Inside_doors','05_Inside_doors',60)]:
  s.frame_set(f);s.camera=bpy.data.objects[cam]
  for ob in ['GC_Removable_drive_guard','GC_Guard_plate']:bpy.data.objects[ob].hide_render=name=='05_Track'
  s.render.filepath=str(out/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
 for ob in ['GC_Removable_drive_guard','GC_Guard_plate']:bpy.data.objects[ob].hide_render=False
 s.frame_set(180);s.camera=bpy.data.objects['01_Cabin_exterior'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Maldek_Gondola_Cabin.blend'))
