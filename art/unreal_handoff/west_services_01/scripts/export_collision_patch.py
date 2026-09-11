import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parents[1];D=json.loads((P/'exports.json').read_text());bpy.ops.wm.open_mainfile(filepath=D['source']);s=bpy.context.scene;s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get()
seals=['WSE_Door_seal','WSE_Door_seal.001','WSE_Door_head_seal'];by={r['key']:r for r in D['assets']};fixed=by['WSE_ASSETS_-10_0'];hardware=by['NONBLOCK_Hardware_-10_0']
for n in seals:
 if n in fixed['sources']:fixed['sources'].remove(n)
 if n not in hardware['sources']:hardware['sources'].append(n)
changed=['WSE_ASSETS_-10_0','NONBLOCK_Hardware_-10_0','WSE_ASSETS_-9_-1']
for key in changed:
 r=by[key];obs=[];M=Matrix(r['matrix'])
 for n in r['sources']:
  o=s.objects[n];me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);me.transform(o.matrix_world)
  if n=='WSE_Fuel_supply':
   for v in me.vertices:v.co.y+=.55*max(0,min(1,(v.co.z-1.82)/.24))
  me.transform(M.inverted());ob=bpy.data.objects.new('PATCH',me);s.collection.objects.link(ob);obs.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=r['mesh'];r['materials']=[m.name for m in ob.data.materials];r['lo']=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];r['hi']=[max(v.co[j] for v in ob.data.vertices) for j in range(3)]
 file=P/'fbx'/(r['mesh']+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE');r['sha256']=hashlib.sha256(file.read_bytes()).hexdigest();bpy.data.objects.remove(ob,do_unlink=True)
r=by['WSP_Door_hinge'];c=r['control']['collisions'][0];c['center'][1]+=.0125;c['extent'][1]-=.0125
by['WSE_Engine_cover_hinge']['control']['angle']=100
D['integration_repairs'].update(engine_cover_degrees=100,fuel_supply_reroute={'y_shift_max_m':.55,'start_station_z':1.82,'end_station_z':2.06},parcels_hinge_collision_inset_m=.025)
D['integration_repairs']['nonblocking_hardware']=sorted(set(D['integration_repairs']['nonblocking_hardware']+seals));(P/'exports.json').write_text(json.dumps(D,indent=2));(P/'collision_patch.json').write_text(json.dumps({'mesh_keys':changed,'configuration_keys':['WSP_Door_hinge','WSE_Engine_cover_hinge'],'repairs':D['integration_repairs']},indent=2));print('PATCHED',changed)
