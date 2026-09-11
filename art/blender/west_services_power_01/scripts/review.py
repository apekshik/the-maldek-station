import bpy,json,math,hashlib,bmesh,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];O=Vector((-37.45,-5,1.2));SRC=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend'
def apply_patch():
 ob=bpy.data.objects['WS_BaseSouth'];before=len(ob.data.polygons)
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.157,depth=.5,location=(2.25,.125,1.95));cut=bpy.context.object;cut.rotation_euler[0]=math.pi/2
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('WSE sleeve aperture ONLY','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 return {'object':'WS_BaseSouth','operation':'cylindrical DIFFERENCE','world_axis':'Y','world_center':[-35.2,-4.875,3.15],'radius_m':.157,'cutter_depth_m':.5,'aperture_world_bounds':[[-35.357,-5,2.993],[-35.043,-4.75,3.307]],'faces_before':before,'faces_after':len(ob.data.polygons),'note':'Only in review. Replay this narrowly scoped cutter on shared south wall during integration. 7 mm radial sleeve clearance; firestop specification deferred.'}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Emergency_Power.blend'));s=bpy.context.scene;s.name='WSE_Fitted_Review'
 with bpy.data.libraries.load(str(SRC),link=False) as (a,b):b.collections=['WS_SHARED_STRUCTURE','WS_SHARED_ROOF','WS_PARCELS_PROXY','WS_RESCUE_PROXY']
 ctx=[]
 for c in b.collections:
  s.collection.children.link(c)
  for ob in c.all_objects:
   w=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=w;ob.location-=O;ctx.append(ob)
 bpy.context.view_layer.update();patch=apply_patch();(P/'shell_patch.json').write_text(json.dumps(patch,indent=2))
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('Neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.42,.45,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 s.view_settings.view_transform='AgX'
 for pos,power,size in [((2,5,8),2000,7),((-5,4,5),1400,6),((5,1,3),700,4)]:
  data=bpy.data.lights.new('Review_softbox','AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Review_softbox',data);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((2.8,4,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('Review_camera');cam=bpy.data.objects.new('Review_camera',data);s.collection.objects.link(cam);s.camera=cam
 def cutaway():
  for ob in ctx:
   pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];zmin=min(v.z for v in pts);ob.hide_render=not ob.name.startswith(('WS_BaseSlab','WS_BaseWest','WS_BaseSouth'))
 def view(n,pos,target,scale,cut=True):
  if cut:cutaway()
  else:
   for ob in ctx:ob.hide_render=False
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;s.render.filepath=str(P/'reviews'/f'{n}.png');(bpy.ops.render.render(write_still=True) if '--skip-renders' not in sys.argv else None)
 view('01_neutral_overview',(11,15,11),(2.6,4.8,1.1),12)
 for ob in bpy.data.objects:
  if ob.name.startswith(('WSE_Distribution','WSE_Transfer','WSE_Circuit','WSE_AC_feed')):ob.hide_render=True
 view('02_service_side',(3.8,5.2,2.7),(2.8,2.8,.85),4.7)
 for ob in bpy.data.objects:
  if ob.name.startswith(('WSE_Distribution','WSE_Transfer','WSE_Circuit','WSE_AC_feed')):ob.hide_render=False
 view('03_controls_stopped',(3.45,5.8,1.75),(3.45,3.4,1.47),1.7)
 # state view, static presentation only
 run=bpy.data.materials['WSE_Run'];p=run.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.05,.6,.1,1);p.inputs['Emission Strength'].default_value=2
 for ob in bpy.data.objects:
  if ob.name.startswith('WSE_Needle'):ob.rotation_euler[1]=.55
 view('04_controls_running_indication',(3.45,5.8,1.75),(3.45,3.4,1.47),1.7)
 p.inputs['Emission Strength'].default_value=0
 for ob in bpy.data.objects:
  if ob.name.startswith('WSE_Needle'):ob.rotation_euler[1]=-.7
 view('05_west_entrance_closed',(-5,8.9,2),(0,7.15,1.35),4.2,False)
 assembly=json.loads((P/'assembly.json').read_text())
 for m in assembly['mechanisms']:
  ob=bpy.data.objects[m['pivot']];ob.rotation_euler['XYZ'.index(m['axis'])]=math.radians(m['open_degrees'])
 view('06_open_mechanisms',(10,14,9),(3.2,5.8,1.15),10)
 view('07_west_entrance_open',(-3.8,7.2,1.7),(1.9,7.2,1.2),4.8,False)
 view('08_louvre_section',(-3,5.8,3.6),(.7,2.7,1.2),5.6)
 # Temporary section cutter affects the fitted render only; remove modifier afterwards.
 duct=bpy.data.objects['WSE_Discharge_duct']
 bpy.ops.mesh.primitive_cube_add(size=1,location=(.6,3.25,1.8));cutter=bpy.context.object;cutter.dimensions=(3.5,1.7,2);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cutter.hide_render=True
 mod=duct.modifiers.new('Review section ONLY','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
 view('09_duct_cutaway',(3,6,4),(.8,2.1,1.05),4.5)
 duct.modifiers.remove(mod);bpy.data.objects.remove(cutter,do_unlink=True)
 view('10_entire_exhaust',(-5,-9,7),(2.25,-.1,3.85),11.8)
 view('11_sleeve_detail',(4,-1.8,2.8),(2.25,.05,1.95),1.4)
 view('13_distribution_open',(2,6.8,1.9),(5.25,6.65,1.4),3.4)
 view('14_battery_open',(4.9,4.7,2.1),(4.9,3.05,.55),2.4)
 # actual player height inside room, perspective
 cutaway();cam.location=(2,7.2,1.65);cam.rotation_euler=(Vector((3.3,3.2,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='PERSP';data.lens=24;s.render.filepath=str(P/'reviews/12_player_height.png');(bpy.ops.render.render(write_still=True) if '--skip-renders' not in sys.argv else None)
 for m in assembly['mechanisms']:bpy.data.objects[m['pivot']].rotation_euler=(0,0,0)
 cutaway();data.type='ORTHO';data.ortho_scale=12;cam.location=(11,15,11);cam.rotation_euler=(Vector((2.6,4.8,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
 s['reference_source_sha256']=hashlib.sha256(SRC.read_bytes()).hexdigest();s['context_transform']='Reference shifted by -origin for local review only; asset append at +origin during integration'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Emergency_Power_Fitted.blend'))





