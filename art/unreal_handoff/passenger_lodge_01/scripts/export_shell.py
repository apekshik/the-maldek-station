"""Static shell pilot; never modify the integrated source or moving assemblies."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'fbx';dest.mkdir(exist_ok=True)
source=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
kind='Deck' if '--deck' in sys.argv else 'Shell'
allowed={'PL02_New_Deck_Rails_and_Stair','PL03_Open_Grating','VF07_Public_Guards','VF07_Deck_Structure'} if kind=='Deck' else {'PL02_Fitted_Lodge_Geometry','PLSH_Shell_Trim','PL03_Corrugated_Exterior','PL03_Removable_Roof'}
deps=bpy.context.evaluated_depsgraph_get();groups={};materials={}
for src in list(bpy.context.scene.objects):
 shifted=kind=='Deck' and src.name.startswith('PL02_Shifted_')
 if src.type!='MESH' or src.hide_render or not src.visible_get() or not (shifted or any(c.name in allowed for c in src.users_collection)):continue
 me=bpy.data.meshes.new_from_object(src.evaluated_get(deps),depsgraph=deps);me.transform(src.matrix_world)
 center=sum((v.co for v in me.vertices),Vector())/len(me.vertices)
 category='ShiftedArrival' if shifted else next(c.name for c in src.users_collection if c.name in allowed)
 key=(category,math.floor(center.x/8),math.floor(center.y/8))
 ob=bpy.data.objects.new('export_'+src.name,me);bpy.context.collection.objects.link(ob)
 groups.setdefault(key,[]).append((ob,src.name))
 for m in me.materials:
  if not m or m.name in materials:continue
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
  materials[m.name]={'color':list(bs.inputs['Base Color'].default_value if bs else m.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value if bs else m.roughness),'metallic':float(bs.inputs['Metallic'].default_value if bs else m.metallic),'pilot_only':True}
rows=[]
for i,(key,group) in enumerate(sorted(groups.items())):
 bpy.ops.object.select_all(action='DESELECT')
 for ob,_ in group:ob.select_set(True)
 bpy.context.view_layer.objects.active=group[0][0];bpy.ops.object.join();ob=bpy.context.object
 name=f'SM_Lodge_{kind}_{i:03d}';ob.name=name
 lo=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];hi=[max(v.co[j] for v in ob.data.vertices) for j in range(3)]
 pivot=[key[1]*8,key[2]*8,4]
 for v in ob.data.vertices:v.co-=Vector(pivot)
 ob.data.update()
 bpy.ops.export_scene.fbx(filepath=str(dest/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
 rows.append({'name':name,'pivot':pivot,'lo':lo,'hi':hi,'sources':[n for _,n in group],'category':key[0],'materials':[m.name if m else None for m in ob.data.materials]})
 bpy.data.objects.remove(ob,do_unlink=True)
(OUT/(kind.lower()+'_exports.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assets':rows,'materials':materials},indent=2))
print('SHELL_EXPORT_COMPLETE',len(rows),flush=True)
