"""Small roof-mounted red lenses surveyed against the approved crowned gondola roof."""
import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
from mathutils.bvhtree import BVHTree
source,deps=load_source();roof=bpy.data.objects['R04_Crowned_Roof'];tree=BVHTree.FromObject(roof,deps);inv=roof.matrix_world.inverted();points=[]
for x in [-1.5,1.5]:
 for y in [5.25,6.65,8.05,9.45,10.85]:
  hit,n,index,distance=tree.ray_cast(inv@Vector((x,y,7)),inv.to_3x3()@Vector((0,0,-1)))
  assert hit is not None
  p=roof.matrix_world@hit;points.append(list(p))
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
materials=[]
for name,color,metal,rough in [('Marker_Base',(.025,.029,.031,1),.8,.3),('Marker_Red_Lens',(.3,.002,.001,1),.05,.2)]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if 'Lens' in name:p.inputs['Emission Color'].default_value=(1,.003,.001,1);p.inputs['Emission Strength'].default_value=3
 materials.append(m)
objects=[];pivot=Vector((0,8.05,4))
for x,y,z in points:
 for name,radius,depth,height,material in [('Base',.045,.015,.0075,materials[0]),('Lens',.034,.024,.022,materials[1])]:
  pos=Vector((x,y,z+height))-pivot
  if name=='Base':bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=depth,location=pos)
  else:
   bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=1,location=pos);bpy.context.object.scale=(radius,radius,depth)
  o=bpy.context.object;o.name='Roof_Marker_'+name;o.data.materials.append(material);objects.append(o)
  for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name='SM_Gondola_Roof_Markers';scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
out=OUT/'trim2';fbx=out/'SM_Gondola_Roof_Markers.fbx'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Gondola_Roof_Markers.blend'))
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
(out/'marker_layout.json').write_text(json.dumps({'source_sha256':EXPECTED,'roof_contact_points':points,'pivot':list(pivot),'lens_diameter_cm':6.8,'count':len(points),'fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest()},indent=2))
