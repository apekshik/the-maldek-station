import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'Millford_Service_Cassette.blend'))
parts=list(bpy.data.collections['CASSETTE / editable parts'].objects)
for part in parts:
 if part.type=='CURVE':part.data.bevel_resolution=0
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
 if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in parts if o.type=='MESH')
bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name='SM_ServiceCassette'
bpy.context.scene.cursor.location=(0,0,.0319);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Centered origin gives inspection a stable pivot; preserve the editable source file.
o.location=(0,0,0);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.cube_project(cube_size=.1);bpy.ops.object.mode_set(mode='OBJECT')
materials=[]
for m in o.data.materials:
 m.name='Cassette_'+m.name[:2];bs=m.node_tree.nodes.get('Principled BSDF')
 materials.append({'name':m.name,'color':list(m.diffuse_color)[:3],'metallic':bs.inputs['Metallic'].default_value,'roughness':bs.inputs['Roughness'].default_value,'window':m.name=='Cassette_11'})
bpy.ops.export_scene.fbx(filepath=str(p/'SM_ServiceCassette.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE')
(p/'export_report.json').write_text(json.dumps({'materials':materials,'vertices':len(o.data.vertices),'triangles':sum(len(f.vertices)-2 for f in o.data.polygons),'dimensions':list(o.dimensions)},indent=2))
