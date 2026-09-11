"""Extend the approved tape study to a three-strand crossing and closed cordon."""
import bpy,json,math,ast,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];SOURCE=OUT.parent/'police_tape_01'
for folder in ['previews','exports','previews/motion_frames']:(OUT/folder).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(SOURCE/'scripts'));import simulate
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'Maldek_Police_Tape_Prototype.blend'))
s=bpy.context.scene;data=json.loads((SOURCE/'motion.json').read_text())
tape=bpy.data.collections['01_Tape_animated'];wraps=bpy.data.collections['02_Trunk_wraps'];stage=bpy.data.collections['90_Review_context_ONLY']
m=bpy.data.materials['PoliceTape_Yellow_Black_Plastic'];bark=bpy.data.materials['Context_bark']
for node in ast.parse((SOURCE/'scripts/build.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in ['ribbon_points','make_ribbon','trunk','move_to','camera','collection']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'approved_tape_helpers','exec'))
perimeter=collection('04_Continuous_perimeter');reports=[]
for label,anchors in [('Lower',[(-1.59,-.065,1.00),(1.59,-.065,1.13)]),('Upper',[(-1.59,.065,1.60),(1.59,.065,1.54)])]:
    simulate.ANCHORS=anchors
    motion=simulate.run();retreat=simulate.run(True)
    (OUT/f'motion_{label.lower()}.json').write_text(json.dumps(motion,separators=(',',':')))
    uv_offset=sum(math.dist(motion['frames'][0]['points'][i],motion['frames'][0]['points'][i+1]) for i in range(36))
    for side,lo,hi,offset in [('Left',0,37,0),('Right',37,66,uv_offset)]:
        ob=make_ribbon(f'Tape_{label}_{side}',motion['frames'][0]['points'][lo:hi],tape,offset)
        ob.shape_key_add(name='Basis')
        for frame,record in enumerate(motion['frames'],1):
            key=ob.shape_key_add(name=f'PBD_{frame:03d}')
            for v,co in zip(key.data,ribbon_points(record['points'][lo:hi],frame*.02)):v.co=co
            edge=(hi-lo-1)*3 if lo==0 else 0
            for j,dx in enumerate([-.003,.004,-.001]):key.data[edge+j].co.x+=dx
            for f,value in [(max(0,frame-1),0),(frame,1),(frame+1,0)]:
                key.value=value;key.keyframe_insert('value',frame=f)
        ob['preview_only']='Baked independent chain simulation; no ribbon-to-ribbon collision.'
    for side,x,z in [('Left',-1.8,anchors[0][2]),('Right',1.8,anchors[1][2])]:
        points=[(x+.215*math.cos(i*2*math.pi/64),.215*math.sin(i*2*math.pi/64),z+.009*math.sin(i*.17)) for i in range(81)]
        make_ribbon(f'Wrap_{label}_{side}',points,wraps,.18 if label=='Upper' else .58)
    reports.append({'strand':label,'anchors':anchors,'break_frame':motion['break_frame'],'retreat_break_frame':retreat['break_frame'],'max_segment_error_m':motion['max_segment_error_m']})

# Closed review perimeter around the restricted side of the crossing. The live
# game's station perimeter will use actual tree locations rather than this loop.
nodes=[(-1.8,0,1.28),(-3.6,-.35,1.37),(-4.8,2.5,1.21),(-4.2,6.2,1.43),(-1.9,8,1.26),(2.6,7.6,1.42),(4.8,4.3,1.32),(3.8,.3,1.44),(1.8,0,1.38)]
for index,(x,y,z) in enumerate(nodes[1:-1],1):
    trunk(f'Cordon_anchor_{index:02d}_context',x,y,.205)
    points=[(x+.213*math.cos(i*2*math.pi/64),y+.213*math.sin(i*2*math.pi/64),z+.01*math.sin(i*.16)) for i in range(81)]
    make_ribbon(f'Perimeter_wrap_{index:02d}',points,perimeter,index*.17)
    points=[(x+.22,y+.014*math.sin(i*.24),z-i*.012) for i in range(22)]
    make_ribbon(f'Perimeter_tail_{index:02d}',points,perimeter,index*.31)
for index,(a,b) in enumerate(zip(nodes,nodes[1:])):
    a,b=Vector(a),Vector(b);direction=(b-a).normalized();a+=direction*.214;b-=direction*.214
    points=[]
    for i in range(65):
        t=i/64;p=a.lerp(b,t);p.z-=(.12+.045*(index%3))*math.sin(math.pi*t);points.append(tuple(p))
    make_ribbon(f'Perimeter_span_{index:02d}',points,perimeter,index*.43)

hero=bpy.data.objects['01_Approach'];hero.location=(0,-7.1,1.85);hero.rotation_euler=(Vector((0,.5,1.16))-hero.location).to_track_quat('-Z','Y').to_euler();hero.data.lens=43
overview=camera('04_Cordon_overview',(10,-12,10),(0,3.0,.8),43)
angle=bpy.data.objects['03_Contact_review'];angle.location=(3.3,-6.5,2.7);angle.rotation_euler=(Vector((0,.4,1.1))-angle.location).to_track_quat('-Z','Y').to_euler();angle.data.lens=43
s.camera=hero;s.frame_set(24)
s.render.resolution_x=1440;s.render.resolution_y=810;s.cycles.samples=16
for item in reports:s.timeline_markers.new('TEAR_'+item['strand'],frame=item['break_frame'])
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Police_Cordon_Prototype.blend'))

# Static handoff of all 3 crossing strands and perimeter, excluding review trees.
exports=[];s.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
for source in list(tape.objects)+list(wraps.objects)+list(perimeter.objects):
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(deps),depsgraph=deps)
    ob=bpy.data.objects.new('SM_'+source.name,mesh);s.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(OUT/'exports'/f'{ob.name}.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
    exports.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
assert len(tape.objects)==6
assert all(r['retreat_break_frame'] is None for r in reports)
assert max(r['break_frame'] for r in reports)-min(r['break_frame'] for r in reports)<=6
(OUT/'manifest.json').write_text(json.dumps({'stage':'Blender cordon prototype; no live map edits','crossing_strands':3,'perimeter_spans':8,'perimeter_nodes':nodes,'simulations':reports,'middle_break_frame':data['break_frame'],'exports':exports,'limitations':['No ribbon-to-ribbon collisions in motion study','Perimeter static in this study','No hand animation or audio','Live tree placement and Unreal runtime implementation pending']},indent=2))
for name,frame,cam in [('01_cordon_approach',24,hero),('02_perimeter_overview',24,overview),('03_crossing_open',110,hero)]:
    s.frame_set(frame);s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
s.camera=hero;s.frame_set(24);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Police_Cordon_Prototype.blend'))
print('CORDON_PROTOTYPE_COMPLETE')
