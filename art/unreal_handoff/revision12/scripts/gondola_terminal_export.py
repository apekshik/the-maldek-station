"""Compact terminal return sheaves and supported drive frames; rope-origin pivots."""
import bpy,math,json
from mathutils import Vector
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC'
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
steel=mat('Pylon_Graphite',(.055,.07,.065));galv=mat('Pylon_Galvanized',(.27,.29,.265));paint=mat('Pylon_Faded_Grey_Green',(.26,.31,.28));red=mat('Pylon_Marker_Red',(.7,.008,.004))
def rod(a,c,r,m,name):
 a=Vector(a);c=Vector(c);d=c-a;bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(a+c)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
def path(pts,r,m):
 c=bpy.data.curves.new('Rim','CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;c.resolution_u=1;c.use_fill_caps=True;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,q in zip(s.points,pts):p.co=(*q,1)
 o=bpy.data.objects.new('Sheave_ring',c);bpy.context.collection.objects.link(o);c.materials.append(m);return o
reports=[]
for index,direction in enumerate([-1,1]):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 D=Vector((-2.35,0,2.955));axisY=Vector((0,direction,0));radius=D.length/2;centre=D/2+axisY*5;u=-D.normalized();normal=u.cross(axisY).normalized()
 # Haul rope continues past the dock, around the bullwheel, into the bare return run.
 path([Vector((0,0,0)),axisY*5]+[centre+u*radius*math.cos(a)+axisY*radius*math.sin(a) for a in [j*math.pi/64 for j in range(65)]]+[D],.032,steel)
 for offset in [-.11,.11]:path([centre+normal*offset+(u*math.cos(a)+axisY*math.sin(a))*(radius-.055) for a in [j*math.tau/96 for j in range(97)]],.055,galv)
 for j in range(12):
  a=j*math.tau/12;rod(centre,centre+(u*math.cos(a)+axisY*math.sin(a))*(radius-.12),.085,paint,'Bullwheel_spoke')
 rod(centre-normal*.4,centre+normal*.4,.32,steel,'Drive_hub')
 # Independent shaft bearings transmit the drive load into the terminal portal.
 for side in [-1,1]:
  bearing=centre+normal*side*.45;rod(bearing,Vector((side*3.4,direction*5,3.8)),.22,paint,'Bearing_diagonal')
  rod((side*3.4,direction*5,-5.927),(side*3.4,direction*5,4.2),.32,paint,'Terminal_column')
  rod((side*3.4,direction*5,-5.927),(side*3.4,direction*5,-5.62),.65,galv,'Anchor_flange')
 rod((-3.4,direction*5,4.2),(3.4,direction*5,4.2),.30,steel,'Terminal_header')
 rod((-3.4,direction*5,4.3),(-3.4,direction*5,4.55),.12,red,'Terminal_marker')
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;name='SM_Gondola_Terminal_'+('Millford' if direction<0 else 'Maldek');o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.export_scene.fbx(filepath=str(out/'fbx'/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 reports.append({'name':name,'vertices':len(o.data.vertices),'materials':[m.name for m in o.data.materials]})
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
(out/'terminal_exports.json').write_text(json.dumps(reports,indent=2))
