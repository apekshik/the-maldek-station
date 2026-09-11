import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[4];d=r/'art/unreal_handoff/revision12/police_tape/wrap_fit';rows=json.loads((d/'fitted.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True)
m=bpy.data.materials.new('PoliceTape_YellowBlack');m.use_nodes=True;m.diffuse_color=(.94,.68,.02,1);n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(r/'art/blender/police_tape_01/textures/T_PoliceTape_BaseColor.png'));n.image.pack();bs=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.43
for i,row in enumerate(rows):
 bpy.ops.import_scene.fbx(filepath=row['fitted_fbx']);obs=list(bpy.context.selected_objects)
 for ob in obs:
  if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m);ob.location=(i%4*.6,i//4*.6,0);ob['wrap_actor']=row['wrap'];ob['tree_actor']=row['tree'];ob['export_note']='Reset object location to zero before individual Unreal re-export; grid is for inspection only.'
bpy.ops.wm.save_as_mainfile(filepath=str(d/'Maldek_Bark_Fitted_Wraps.blend'))
