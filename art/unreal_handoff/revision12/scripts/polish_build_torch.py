"""Author a small reusable torch assembly; dimensions in metres, forward is +X."""
import bpy,math,json,hashlib
from mathutils import Vector
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'polish'/'torch';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
for name,color,metal,rough in [('Anodized',(0.032,0.041,0.049),.9,.32),('Grip',(0.021,0.025,0.028),.12,.72),('Machined',(0.29,.32,.34),1,.24),('Reflector',(.63,.67,.7),1,.17),('Lens',(.10,.16,.19),.25,.14),('Switch',(.12,.14,.13),.15,.65)]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;materials[name]=m
objects=[]
def lathe(name,profile,mat,n=96):
 verts=[(x,r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n)) for x,r in profile for i in range(n)]
 faces=[]
 for j in range(len(profile)-1):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(materials[mat]);obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
 objects.append(obj);return obj
lathe('Body',[(0,.020),(.003,.024),(.012,.024),(.016,.022),(.151,.022),(.16,.024),(.178,.024),(.196,.030),(.207,.035),(.239,.035),(.244,.033)],'Anodized')
lathe('TailCap',[(0,.022),(.003,.025),(.012,.025),(.016,.022)],'Machined')
lathe('GripSleeve',[(.024,.023),(.03,.024),(.145,.024),(.15,.023)],'Grip')
for j in range(44):
 a=j*2*math.pi/44
 # Raised fine ribs catch nearby light; actual geometry, not a flat grip texture.
 r=.0242;x=.034;length=.106
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x+length/2,r*math.cos(a),r*math.sin(a)))
 obj=bpy.context.object;obj.name='GripRib';obj.scale=(length,.00065,.00065);obj.data.materials.append(materials['Grip']);objects.append(obj)
for x in [.019,.154,.166,.176,.202,.212,.222,.232]:lathe('GrooveRing',[(x-.0005,.0245 if x<.19 else .0352),(x+.0005,.0245 if x<.19 else .0352)],'Machined')
lathe('Bezel',[(.238,.035),(.240,.0358),(.247,.0358),(.250,.034),(.250,.030),(.247,.0298)],'Machined')
lathe('Reflector',[(.215,.006),(.22,.015),(.235,.026),(.246,.03)],'Reflector')
lathe('Lens',[(.247,.0295),(.248,.0295)],'Lens')
lathe('TailGrip',[(.004,.0254),(.010,.0254)],'Grip')
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=12,location=(.176,0,.026));obj=bpy.context.object;obj.name='Switch';obj.scale=(.009,.006,.003);obj.data.materials.append(materials['Switch']);objects.append(obj)
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();obj=bpy.context.object;obj.name='SM_Torch_Field';bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
tri=obj.modifiers.new('Triangulate','TRIANGULATE');bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=tri.name)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Field_Torch.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Torch_Field.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,mesh_smooth_type='FACE')
(out/'manifest.json').write_text(json.dumps({'mesh':'SM_Torch_Field','length_m':.25,'triangles':len(obj.data.polygons),'slots':[m.name for m in obj.data.materials],'fbx_sha256':hashlib.sha256((out/'SM_Torch_Field.fbx').read_bytes()).hexdigest()},indent=2))
