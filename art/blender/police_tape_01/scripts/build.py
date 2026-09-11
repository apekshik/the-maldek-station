"""Build editable tape, a baked PBD motion study, and static Unreal handoff meshes."""
import bpy, json, math, random
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
data=json.loads((OUT/'motion.json').read_text())
for d in ['previews','exports']: (OUT/d).mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.fps=24;s.frame_end=len(data['frames'])

def collection(name):
    c=bpy.data.collections.new(name);s.collection.children.link(c);return c
tape=collection('01_Tape_animated');wraps=collection('02_Trunk_wraps');stage=collection('90_Review_context_ONLY');controls=collection('03_Controls')
def material(name,color,rough=.5):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
    return m
m=material('PoliceTape_Yellow_Black_Plastic',(.92,.64,.015),.38)
nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
im=bpy.data.images.load(str(OUT/'textures/T_PoliceTape_BaseColor.png'));im.pack()
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.00008
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
p.inputs['Coat Weight'].default_value=.16;p.inputs['Coat Roughness'].default_value=.32

def ribbon_points(points,phase=0):
    result=[]
    for i,point in enumerate(points):
        point=Vector(point);a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)])
        tangent=(b-a).normalized()
        up=Vector((0,0,1));up-=tangent*up.dot(tangent)
        if up.length<.2:up=Vector((1,0,0))-tangent*tangent.x
        up.normalize();side=tangent.cross(up).normalized()
        twist=.13*math.sin(i*.53+phase)+.045*math.sin(i*1.6)
        width=up*math.cos(twist)+side*math.sin(twist)
        for j in range(3):
            v=point+width*(j-1)*data['width_m']/2
            v+=side*(.0007*math.sin(i*1.7+j))
            result.append(tuple(v))
    return result

def make_ribbon(name,points,col,offset=0):
    vs=ribbon_points(points);fs=[]
    for i in range(len(points)-1):
        for j in range(2):
            a=i*3+j;fs.append((a,a+3,a+4,a+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
    ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);mesh.materials.append(m)
    uv=mesh.uv_layers.new(name='TapeLettering')
    lengths=[offset]
    for i in range(1,len(points)): lengths.append(lengths[-1]+(Vector(points[i])-Vector(points[i-1])).length)
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(lengths[vi//3]/1.2192,(vi%3)/2)
    solid=ob.modifiers.new('Physical film thickness 0.076 mm','SOLIDIFY');solid.thickness=.000076;solid.offset=0
    ob['width_m']=data['width_m'];ob['material']='nonadhesive polyethylene study'
    return ob

parts=[]
seam_uv_offset=sum((Vector(data['frames'][0]['points'][i+1])-Vector(data['frames'][0]['points'][i])).length for i in range(36))
for name,lo,hi,offset in [('Tape_Left',0,37,0),('Tape_Right',37,66,seam_uv_offset)]:
    ob=make_ribbon(name,data['frames'][0]['points'][lo:hi],tape,offset);parts.append(ob)
    ob.shape_key_add(name='Basis')
    for frame,record in enumerate(data['frames'],1):
        key=ob.shape_key_add(name=f'PBD_{frame:03d}')
        for v,co in zip(key.data,ribbon_points(record['points'][lo:hi],frame*.02)):v.co=co
        # Matching shallow zig-zag fracture edges, visible only when separated.
        edge=(hi-lo-1)*3 if lo==0 else 0
        for j,dx in enumerate([-.003,.004,-.001]):key.data[edge+j].co.x+=dx
        for f,value in [(max(0,frame-1),0),(frame,1),(frame+1,0)]:
            key.value=value;key.keyframe_insert('value',frame=f)
    ob['preview_only']='Baked simulated positions. Runtime deformation must be implemented in Unreal.'

# Continuous trunk loops tuck behind the outgoing ribbon, with short loose tails.
for side,x,z in [('Left',-1.8,1.28),('Right',1.8,1.38)]:
    pts=[]
    for i in range(97):
        a=2*math.pi*i/64
        pts.append((x+.212*math.cos(a),.212*math.sin(a),z+.015*math.sin(a*2)+.008*i/96))
    make_ribbon('Wrap_'+side,pts,wraps)
    pts=[(x+.219*math.cos(.15+i*.025),.219*math.sin(.15+i*.025),z-i*.012) for i in range(26)]
    make_ribbon('Loose_tail_'+side,pts,wraps,.32)

bark=material('Context_bark',(.065,.075,.057),.94)
bn=bark.node_tree.nodes;bl=bark.node_tree.links;bp=bn.get('Principled BSDF')
ntx=bn.new('ShaderNodeTexNoise');ntx.inputs['Scale'].default_value=19;ntx.inputs['Detail'].default_value=3
bu=bn.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.75;bu.inputs['Distance'].default_value=.022;bl.new(ntx.outputs['Fac'],bu.inputs['Height']);bl.new(bu.outputs['Normal'],bp.inputs['Normal'])
ground=material('Context_forest_floor',(.023,.030,.023),.97)
leaf=material('Context_understorey',(.031,.059,.024),.85)
def move_to(o,col):
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o)
def trunk(name,x,y,r=.20):
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=r,radius2=r*.77,depth=5,location=(x,y,2.45))
    o=bpy.context.object;o.name=name;move_to(o,stage);o.data.materials.append(bark)
    for p in o.data.polygons:p.use_smooth=True
for x in [-1.8,1.8]:trunk('Anchor_tree_context',x,0,.205)
random.seed(1109)
for i in range(18):
    x=random.choice([-1,1])*random.uniform(2.0,5.5);y=random.uniform(1,8)
    trunk('Background_tree_context',x,y,random.uniform(.10,.22))
bpy.ops.mesh.primitive_plane_add(size=200);o=bpy.context.object;o.name='Review_ground';move_to(o,stage);o.data.materials.append(ground)
# Low-cost silhouette context; these are not exportable foliage assets.
for i in range(90):
    x=random.choice([-1,1])*random.uniform(1.55,5);y=random.uniform(-1.2,7)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.16,.38),location=(x,y,random.uniform(.13,.48)))
    o=bpy.context.object;o.name='Understorey_context';o.scale=(1,.7,random.uniform(1,1.8));move_to(o,stage);o.data.materials.append(leaf)

proxy=bpy.data.objects.new('PLAYER_CONTACT_PROXY_radius_31cm',None);controls.objects.link(proxy)
proxy.empty_display_type='SPHERE';proxy.empty_display_size=.31
for frame,record in enumerate(data['frames'],1):
    proxy.location=(.12,record['player_y'],1.2);proxy.keyframe_insert('location',frame=frame)
proxy['note']='Preview contact cylinder; not a rendered player or hand.'
for name,frame in [('INTACT',1),('CONTACT',45),('TEAR',data['break_frame']),('RELEASED',85),('SETTLED',144)]:s.timeline_markers.new(name,frame=frame)

def camera(name,pos,target,lens):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return o
def light(name,pos,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.color=color;d.shape='DISK';d.size=size
light('Soft sky',(-2,-2,6),(0,0,1),950,(.57,.70,1),6)
light('Player-side illumination',(0,-3,2),(0,0,1.2),130,(1,.91,.73),1.5)
light('Forest rim',(2,4,4),(0,0,1),600,(.48,.64,.85),4)
hero=camera('01_Approach',(0,-5.8,1.67),(0,0,1.12),48)
detail=camera('02_Tree_attachment',(-1.10,-1.02,1.54),(-1.74,0,1.27),58)
angle=camera('03_Contact_review',(2.8,-4.8,2.2),(0,.1,1),47)
s.camera=hero;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=810;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Dusk_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.10,.15,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
s.view_settings.view_transform='AgX'
s.frame_set(1)
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Police_Tape_Prototype.blend'))

# Export evaluated static halves and trunk attachments. Animation is in the blend.
bpy.ops.object.select_all(action='DESELECT')
deps=bpy.context.evaluated_depsgraph_get();exported=[]
for source in list(tape.objects)+list(wraps.objects):
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(deps),depsgraph=deps)
    ob=bpy.data.objects.new('SM_'+source.name,mesh);s.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    dest=OUT/'exports'/f'{ob.name}.fbx'
    bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
    exported.append({'name':ob.name,'vertices':len(mesh.vertices),'file':str(dest)})
    bpy.data.objects.remove(ob,do_unlink=True)
(OUT/'manifest.json').write_text(json.dumps({'stage':'Blender prototype; not installed in Unreal','width_m':data['width_m'],'film_thickness_m':.000076,'anchor_span_m':3.18,'break_frame':data['break_frame'],'duration_seconds':6,'fps':24,'simulation':'120 Hz position-based dynamics, anchored endpoints and torso contact; controlled seam release','exports':exported,'reference_sources':['https://www.uline.com/Product/Detail/S-22041/Barricade-Tape/Barricade-Tape-3-x-1000-Police-Line-Do-Not-Cross','https://www.cbsnews.com/sacramento/news/man-found-dead-grass-valley-california-storm/'],'pending':['Unreal runtime ribbon deformation and walking interaction','Source recorded crinkle/tear audio','Live placement, foliage density and traversal checks']},indent=2))
for name,frame,cam in [('01_intact',24,hero),('02_tension',data['break_frame']-1,angle),('03_torn',96,hero),('04_attachment',24,detail)]:
    s.frame_set(frame);s.camera=cam;s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
s.camera=hero;s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Police_Tape_Prototype.blend'))
print('TAPE_PROTOTYPE_COMPLETE',flush=True)
