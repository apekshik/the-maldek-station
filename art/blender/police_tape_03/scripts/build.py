import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];FIRST=OUT.parent/'police_tape_01'
motion=json.loads((OUT/'motion.json').read_text());report=json.loads((OUT/'physics_check.json').read_text())
for f in ['previews','exports','previews/motion_frames']:(OUT/f).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'police_tape_02/Maldek_Police_Cordon_Prototype.blend'))
s=bpy.context.scene;data={'width_m':.0762};m=bpy.data.materials['PoliceTape_Yellow_Black_Plastic']
for node in ast.parse((FIRST/'scripts/build.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in ['ribbon_points','make_ribbon']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'ribbon_helpers','exec'))
tape=bpy.data.collections['01_Tape_animated'];wraps=bpy.data.collections['02_Trunk_wraps']
for ob in list(tape.objects)+list(wraps.objects):bpy.data.objects.remove(ob,do_unlink=True)
names=['Rising','Falling','Middle']
for k,name in enumerate(names):
    points=motion['frames'][0][k];offset=sum(math.dist(points[i],points[i+1]) for i in range(36))
    for side,lo,hi,uv in [('Left',0,37,0),('Right',37,66,offset)]:
        ob=make_ribbon(f'Tape_{name}_{side}',points[lo:hi],tape,uv);ob.shape_key_add(name='Basis')
        for f,allpoints in enumerate(motion['frames'],1):
            key=ob.shape_key_add(name=f'Coupled_{f:03d}')
            for v,co in zip(key.data,ribbon_points(allpoints[k][lo:hi],f*.02)):v.co=co
            edge=(hi-lo-1)*3 if lo==0 else 0
            for j,dx in enumerate([-.003,.004,-.001]):key.data[edge+j].co.x+=dx
            for frame,value in [(f-1,0),(f,1),(f+1,0)]:key.value=value;key.keyframe_insert('value',frame=frame)
        ob['physics']='Coupled ribbon contact proxy study, baked into shape keys'
    for side,tx,anchor in [('Left',-1.8,report['anchors'][k][0]),('Right',1.8,report['anchors'][k][1])]:
        points=[(tx+.215*math.cos(i*2*math.pi/64),.215*math.sin(i*2*math.pi/64),anchor[2]+.008*math.sin(i*.17)) for i in range(81)]
        make_ribbon(f'Wrap_{name}_{side}',points,wraps,k*.26)
        tail=[(tx+.22,.015*math.sin(i*.25),anchor[2]-i*.01) for i in range(20)]
        make_ribbon(f'Tail_{name}_{side}',tail,wraps,k*.31)
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for name,f in [('INTACT',24),('CONTACT',48),('RELEASED',96)]+[(f'TEAR_{n}',f) for n,f in zip(names,motion['break_frames'])]:s.timeline_markers.new(name,frame=f)
hero=bpy.data.objects['01_Approach'];angle=bpy.data.objects['03_Contact_review']
s.camera=hero;s.frame_set(24);s.cycles.samples=16
s.render.resolution_x=1440;s.render.resolution_y=810
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Crisscross_Cordon.blend'))
s.frame_set(24);deps=bpy.context.evaluated_depsgraph_get()
for source in list(tape.objects)+list(wraps.objects):
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(deps),depsgraph=deps);ob=bpy.data.objects.new('SM_'+source.name,mesh);s.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(OUT/'exports'/f'{ob.name}.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
    bpy.data.objects.remove(ob,do_unlink=True)
checks=[]
for frame in [24,56,64,96,144]:
    s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();inside=0
    for ob in tape.objects:
        ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        inside+=sum(abs(v.co.x)<.65 and v.co.z>.2 for v in mesh.vertices);ev.to_mesh_clear()
    if frame>=96:assert inside==0,(frame,inside)
    checks.append({'frame':frame,'vertices_in_walking_gap':inside})
(OUT/'verification.json').write_text(json.dumps({'passed':True,'checks':checks,'crossing_strands':3,'perimeter_spans':8,'static_crossing_exports':18},indent=2))
for name,frame,cam in [('01_crisscross',24,hero),('02_contact',min(motion['break_frames'])-1,angle),('03_released',110,hero)]:
    s.camera=cam;s.frame_set(frame);s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
s.camera=hero;s.frame_set(24);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Crisscross_Cordon.blend'))
s.camera=angle;s.cycles.samples=8;s.render.resolution_x=800;s.render.resolution_y=450
s.frame_step=3;s.render.filepath=str(OUT/'previews/motion_frames/frame_');bpy.ops.render.render(animation=True)
print('CRISSCROSS_COMPLETE')
