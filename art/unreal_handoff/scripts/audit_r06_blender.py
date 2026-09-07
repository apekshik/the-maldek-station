import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'revision06';out.mkdir(exist_ok=True);(out/'fbx').mkdir(exist_ok=True)
report={}
for o in bpy.data.objects:
 if o.type=='MESH' and ('Terrain_Cliff' in o.name or o.name.startswith('Pine_CC0_') and o.name in ['Pine_CC0_0','Pine_CC0_1','Pine_CC0_2']):
  report[o.name]={'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':[m.name for m in o.data.materials],'bounds':[list(o.matrix_world@Vector(p)) for p in o.bound_box]}
  if 'Pine_CC0' in o.name:
   bpy.ops.object.select_all(action='DESELECT');copy=bpy.data.objects.new('SM_R06_Pine_'+o.name[-1],o.data.copy());bpy.context.collection.objects.link(copy);copy.select_set(True);bpy.context.view_layer.objects.active=copy
   modifier=copy.modifiers.new('Game_Density','DECIMATE');modifier.ratio=.18;bpy.ops.object.modifier_apply(modifier=modifier.name)
   bpy.ops.export_scene.fbx(filepath=str(out/'fbx'/(copy.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE');bpy.data.objects.remove(copy,do_unlink=True)
report['materials']={m.name:[{'image':n.image.name,'filepath':n.image.filepath} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] for m in bpy.data.materials if 'pine' in m.name.lower() and m.use_nodes}
(out/'blender_reference.json').write_text(json.dumps(report,indent=2))

