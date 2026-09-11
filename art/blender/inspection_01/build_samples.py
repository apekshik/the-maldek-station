"""Editable, metre-scale inspection prop. Run in a separate background Blender process."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'

def material(name,color,metal=0,rough=.45):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
green=material('Meter_Enamel',(.045,.105,.087),.55,.34)
rubber=material('Meter_Rubber',(.013,.019,.02),0,.7)
brass=material('Meter_Brass',(.48,.31,.105),.8,.28)
paper=material('Meter_Ivory',(.78,.72,.51),0,.62)
ink=material('Meter_Ink',(.017,.023,.022),0,.65)
red=material('Meter_Red',(.46,.027,.018),.3,.36)
parts=[]
def finish(obj,name,mat,bevel=0):
 obj.name=name;obj.data.materials.append(mat)
 if bevel:
  mod=obj.modifiers.new('Machined edges','BEVEL');mod.width=bevel;mod.segments=3
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
 parts.append(obj);return obj
def box(name,loc,size,mat,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,name,mat,bevel)
def cylinder(name,loc,radius,depth,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc,rotation=(math.pi/2,0,0))
 return finish(bpy.context.object,name,mat,.0006)
def text(name,body,loc,size,mat,back=False):
 bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,math.pi if back else 0))
 o=bpy.context.object;o.data.body=body;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.00008
 bpy.ops.object.convert(target='MESH');return finish(bpy.context.object,name,mat)

box('Impact bumper',(0,0,.12),(.166,.078,.24),rubber,.009)
box('Green steel shell',(0,-.006,.12),(.156,.071,.228),green,.007)
box('Rear cover',(0,.04,.12),(.142,.005,.21),green,.005)
box('Face bezel',(0,-.044,.156),(.133,.011,.116),brass,.005)
box('Dial paper',(0,-.0505,.156),(.123,.003,.106),paper,.003)
for i in range(21):
 angle=math.radians(25+i*6.5)
 x=.047*math.cos(angle);z=.137+.047*math.sin(angle)
 mark=box('Scale division',(x,-.0525,z),(.0011,.001,.007 if i%5==0 else .0035),ink,.0001)
 mark.rotation_euler[1]=math.pi/2-angle
needle=box('Red needle',(.008,-.054,.16),(.0016,.001,.048),red,.0002);needle.rotation_euler[1]=-.32
cylinder('Needle pivot',(0,-.055,.136),.004,.003,brass)
text('Dial units','TENSION / kN',(0,-.054,.122),.007,ink)
text('Dial numbers','0     5     10',(0,-.054,.178),.007,ink)
cylinder('Selector collar',(0,-.045,.064),.024,.007,brass)
cylinder('Selector grip',(0,-.053,.064),.019,.012,rubber)
box('Selector marker',(0,-.060,.076),(.002,.001,.008),paper,.0001)
text('Brand','MILLFORD',(0,-.044,.217),.009,paper)
text('Mode','OFF     TEST',(0,-.044,.029),.006,paper)
for x in [-.061,.061]:
 for z in [.023,.217]:
  cylinder('Slotted screw',(x,-.043,z),.003,.002,brass)
  box('Screw slot',(x,-.0445,z),(.004,.0004,.0006),ink,.0001)
box('Rear serial plate',(0,.044,.155),(.108,.003,.056),brass,.001)
text('Rear service marking','SERVICE  /  1986',(0,.046,.165),.007,ink,True)
text('Rear serial','MS - 0147',(0,.046,.146),.01,ink,True)
for z in [.058,.067,.076,.085]:box('Rear cooling slot',(0,.044,z),(.09,.002,.003),rubber,.001)
for x in [-.046,.046]:
 box('Handle foot',(x,0,.247),(.013,.025,.025),brass,.003)
box('Carry handle',(0,0,.267),(.105,.023,.014),rubber,.005)

# Join all visible pieces to one mesh, with independent material slots and a floor origin.
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
obj=bpy.context.object;obj.name='SM_InspectionMeter'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Inspection_Meter.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'SM_InspectionMeter.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
(OUT/'build_report.json').write_text(json.dumps({'mesh':obj.name,'vertices':len(obj.data.vertices),'dimensions_metres':list(obj.dimensions),'materials':[m.name for m in obj.data.materials]},indent=2))
