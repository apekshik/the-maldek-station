"""Blender shape-only review of original exported library meshes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
b=Path(__file__).resolve().parents[1]/'forest_refine'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
files=sorted((b/'rocks').glob('*.fbx'))+sorted((b/'vehicles').glob('*.fbx'));report=[]
for i,f in enumerate(files):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(f));objs=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
 # Exporter includes LODs: inspect the first/highest resolution mesh only.
 ob=max(objs,key=lambda o:len(o.data.polygons))
 for other in objs:
  if other!=ob:bpy.data.objects.remove(other,do_unlink=True)
 bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=world;bpy.context.view_layer.update()
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=Vector([min(p[j] for p in pts) for j in range(3)]);hi=Vector([max(p[j] for p in pts) for j in range(3)])
 dim=hi-lo;scale=3.4/max(dim.x,dim.y,dim.z);ob.scale*=scale;ob.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))*scale
 ox=(i%4)*5;oy=-(i//4)*5;ob.location+=Vector((ox,oy,0));ob.color=(.34,.39,.36,1)
 report.append({'name':f.stem,'dimensions':list(dim),'vertices':len(ob.data.vertices)})
 curve=bpy.data.curves.new(f.stem,'FONT');curve.body=f.stem;curve.size=.28;curve.align_x='CENTER';label=bpy.data.objects.new(f.stem+'_label',curve);bpy.context.collection.objects.link(label);label.location=(ox,oy-2.1,.01)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.world.color=(.06,.06,.06)
bpy.ops.object.camera_add(location=(10,-19,24));cam=bpy.context.object;cam.rotation_euler=(Vector((7.5,-5,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=22;scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.filepath=str(b/'asset_shapes.png');bpy.ops.render.render(write_still=True)
(b/'asset_shapes.json').write_text(json.dumps(report,indent=2))
