import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P.parents[1]/'blender/station_dressing_01/Maldek_Station_Furnished.blend'));s=bpy.context.scene;s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();plan=json.loads((P/'deck_replacement_plan.json').read_text());rows=[]
for r in plan['chunks']:
 obs=[]
 for name in r['sources']:
  if name in plan['retired']:continue
  o=s.objects[name];me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);me.transform(o.matrix_world);me.transform(__import__('mathutils').Matrix.Translation(-Vector(r['pivot'])));ob=bpy.data.objects.new('EXP',me);s.collection.objects.link(ob);obs.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=r['name'].replace('SM_Lodge','SM_WS_Lodge');fp=P/'fbx'/(ob.name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(fp),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
 rows.append({'old':r['name'],'new':ob.name,'materials':[m.name for m in ob.data.materials],'old_materials':r['materials'],'retired':[n for n in r['sources'] if n in plan['retired']],'preserved':[n for n in r['sources'] if n not in plan['retired']]});bpy.data.objects.remove(ob,do_unlink=True)
(P/'deck_patch_exports.json').write_text(json.dumps(rows,indent=2))
