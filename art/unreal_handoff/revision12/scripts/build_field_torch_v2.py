"""Reference-led field torch, metres, +X forward. Separate editable Blender source."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'sensory_refine'/'torch_v2';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
parts=[];mats={}
specs=[('Anodized',(.018,.023,.028),.85,.29),('Grip',(.015,.019,.023),.75,.42),
 ('Machined',(.32,.36,.4),1,.23),('Reflector',(.74,.77,.8),1,.12),
 ('Lens',(.075,.11,.13),.30,.10),('Switch',(.012,.014,.017),.03,.70),
 ('Markings',(.34,.36,.33),.15,.56)]
for name,col,metal,rough in specs:
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1)
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if name=='Lens':
  p.inputs['Metallic'].default_value=0;p.inputs['Transmission Weight'].default_value=1;p.inputs['Roughness'].default_value=.025;p.inputs['IOR'].default_value=1.48
 mats[name]=m
def mesh(name,verts,faces,mat,smooth=True):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.materials.append(mats[mat]);data.update()
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);parts.append(obj)
 for p in data.polygons:p.use_smooth=smooth and len(p.vertices)==4
 return obj
def lathe(name,profile,mat,n=96,closed=False):
 verts=[(x,r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n)) for x,r in profile for i in range(n)]
 faces=[]
 for j in range(len(profile) if closed else len(profile)-1):
  k=(j+1)%len(profile)
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,k*n+(i+1)%n,k*n+i))
 if not closed:faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
 return mesh(name,verts,faces,mat)
def box(name,p,size,mat,bevel=.0008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);obj=bpy.context.object;obj.name=name;obj.scale=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mats[mat])
 if bevel:
  mod=obj.modifiers.new('Machined edge radii','BEVEL');mod.width=bevel;mod.segments=3
  bpy.ops.object.modifier_apply(modifier=mod.name)
 parts.append(obj);return obj
# 231.8 mm length, 38.1 mm barrel and 57.15 mm head, based on ML300L 2D proportions.
lathe('Battery_barrel',[(.010,.0181),(.012,.0187),(.027,.0187),(.030,.0186),(.139,.0186),(.142,.01905),(.166,.01905),(.170,.0188)],'Anodized')
lathe('Tail_cap',[(0,.0175),(.001,.0188),(.003,.0191),(.012,.0191),(.014,.0187)],'Anodized')
lathe('Tail_seal',[(.0138,.01874),(.0144,.01874)],'Switch')
# Machined cross-hatched grip: continuous diamonds, with no long raised rod ribs.
verts=[];faces=[];nx=112;na=128
for j in range(nx+1):
 x=.033+j/nx*.103
 for i in range(na):
  a=i*math.tau/na
  u=j/2+i/4;v=j/2-i/4
  ridge=(abs(math.sin(math.pi*u))*abs(math.sin(math.pi*v)))**.7
  r=.0189+.00030*ridge
  verts.append((x,r*math.cos(a),r*math.sin(a)))
for j in range(nx):
 for i in range(na):faces.append((j*na+i,j*na+(i+1)%na,(j+1)*na+(i+1)%na,(j+1)*na+i))
mesh('Diamond_knurled_grip',verts,faces,'Grip')
for x in [.028,.030,.139,.141]:lathe('Grip_end_cut',[(x,.0191),(x+.00045,.0191)],'Anodized')
for j in range(72):
 a=j*math.tau/72
 obj=box('Tail_flute',(.0065,.01905*math.cos(a),.01905*math.sin(a)),(.005,.0007,.0006),'Grip',.00015)
 obj.rotation_euler.x=a
# Defined shoulder taper and cylindrical bezel replace the oversize rounded head.
lathe('Focus_head',[(.165,.0192),(.17,.0195),(.177,.021),(.186,.0245),(.194,.0267),(.201,.0277),(.207,.0281),(.221,.0281),(.223,.0278)],'Anodized')
lathe('Focus_seam',[(.165,.0193),(.166,.0193)],'Switch')
lathe('Bezel_outer',[(.2225,.0279),(.2235,.028575),(.2305,.028575),(.2318,.0280),(.2318,.0259),(.2308,.0255),(.224,.0255)],'Anodized',closed=True)
lathe('Bezel_contact_edge',[(.231,.0259),(.2318,.0259),(.2318,.0254),(.231,.0254)],'Machined',closed=True)
lathe('Reflector_bowl',[(.207,.004),(.209,.007),(.213,.012),(.218,.017),(.224,.022),(.229,.0252),(.229,.0255),(.223,.0223),(.217,.0173),(.212,.0123),(.208,.0073),(.2068,.004)],'Reflector',closed=True)
lathe('LED_carrier',[(.206,.004),(.208,.004)],'Machined',n=48)
box('LED_emitter',(.2084,0,0),(.0006,.003,.003),'Markings',.0001)
# Thin optical face is retained as a separate slot for the Unreal optical material.
lathe('Optical_window',[(.2296,.02525),(.2301,.02525)],'Lens')
switch=box('Recessed_switch_surround',(.156,0,.01865),(.017,.013,.002),'Anodized',.001)
box('Flat_rubber_switch',(.156,0,.01965),(.0118,.0088,.0012),'Switch',.00065)
for x in [.153,.156,.159]:box('Switch_tactile_line',(x,0,.0203),(.00045,.004,.00016),'Grip',.00005)
# Small service engraving; original in-game branding, no copied manufacturer logo.
for text,x,y,size in [('MALDEK / FIELD 02',.095,-.0015,.0025)]:
 curve=bpy.data.curves.new('Engraving','FONT');curve.body=text;curve.size=size;curve.extrude=.000015
 obj=bpy.data.objects.new('Service_marking',curve);bpy.context.collection.objects.link(obj)
 obj.location=(x,y,.01935);obj.data.materials.append(mats['Markings'])
 bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False);parts.append(bpy.context.object)
# Keep named individual parts in the source; export a joined duplicate for the engine.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.duplicate();bpy.ops.object.join();export=bpy.context.object;export.name='SM_Torch_Field_V2'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=export.modifiers.new('Export triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
# Recalculate consistent exterior normals after all authored parts have been joined.
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
assert .231<export.dimensions.x<.233 and .057<export.dimensions.y<.058
export['reference']='https://maglite.com/products/ml300l-led-2-cell-d-flashlight'
export['axis']='Forward +X; metres; tail origin'
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Torch_Field_V2.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,mesh_smooth_type='FACE')
for obj in parts:obj.hide_render=True;obj.hide_set(True)
# Neutral product views make the silhouette, switch and grip inspectable before import.
s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1400;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral studio');s.world.color=(.12,.12,.12)
def area(name,p,energy,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
 obj=bpy.data.objects.new(name,data);s.collection.objects.link(obj);obj.location=p;obj.rotation_euler=(Vector((.115,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
area('Key',(.1,-.18,.25),12,.24);area('Edge',(.2,.15,.08),9,.18);area('Front',(.36,-.08,.05),5,.12)
data=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',data);s.collection.objects.link(cam);s.camera=cam;data.type='ORTHO';data.ortho_scale=.31
cam.location=(.33,-.40,.25);cam.rotation_euler=(Vector((.115,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(out/'torch_review.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'Field_Torch_V2.blend'));bpy.ops.render.render(write_still=True)
report={'source':'Field_Torch_V2.blend','mesh':export.name,'dimensions_m':list(export.dimensions),'triangles':len(export.data.polygons),'slots':[m.name for m in export.data.materials],'parts':len(parts),'reference':export['reference'],'fbx_sha256':hashlib.sha256((out/'SM_Torch_Field_V2.fbx').read_bytes()).hexdigest()}
(out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
