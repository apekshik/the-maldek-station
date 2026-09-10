"""Final fitted refinements and representative editable mechanism poses."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen.blend'))
s=bpy.data.scenes['PLK_Fitted_Review'];bpy.context.window.scene=s
hand=bpy.data.objects['PLK_Hand_basin'];hand.location=(4.46,-13.24,.86);hand.rotation_euler.z=math.pi
bpy.data.objects['PLK_Waste_bin'].location=(4.48,-12.62,0)
# Face all front labels outward (+Y in their component basis).
for obj in bpy.data.collections['PLK_Assets'].all_objects:
 if obj.type=='FONT' and abs(obj.rotation_euler.z)<.01:obj.rotation_euler.z=math.pi
# Replace the small draft microwave pull with a full-height bow handle.
old=bpy.data.objects.get('PLK_Microwave_Handle')
if old:bpy.data.objects.remove(old,do_unlink=True)
cu=bpy.data.curves.new('PLK_Microwave_Handle','CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(3)
for pt,xyz in zip(sp.points,[(.367,.033,.07),(.367,.06,.08),(.367,.06,.21),(.367,.033,.22)]):pt.co=(*xyz,1)
obj=bpy.data.objects.new('PLK_Microwave_Handle',cu);bpy.data.collections['PLK_Assets'].objects.link(obj);obj.parent=bpy.data.objects['PLK_Microwave_Door_Pivot'];cu.materials.append(bpy.data.materials['PLK_Bakelite_rubber'])
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
import bmesh
bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
# Closed bracket loops use cyclic curves rather than two meeting capped ends.
for n,x in [('PLK_Shelf_Bracket',.1),('PLK_Shelf_Bracket.001',1.0)]:
 old=bpy.data.objects.get(n)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(2);sp.use_cyclic_u=True
 for p,xyz in zip(sp.points,[(x,.01,-.25),(x,.01,-.02),(x,.30,-.02)]):p.co=(*xyz,1)
 o=bpy.data.objects.new(n,cu);bpy.data.collections['PLK_Assets'].objects.link(o);o.parent=bpy.data.objects['PLK_Wall_shelf'];cu.materials.append(bpy.data.materials['PLK_Brushed_stainless'])
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Remove two diagnosed duplicate/intruding construction members.
for name in ['PLK_Serving_Back','PLK_Wash_base_Top_rail.001','PLK_Prep_drawers_Shelf.001']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.collections['PLK_Assets'].all_objects:
 if o.name.startswith('PLK_Hand_Bracket') and not o.get('below_bowl'):
  o.location.z-=.17;o['below_bowl']=True
 if o.name.startswith('PLK_Fridge_Shelf_support') and not o.get('rack_clearance'):
  for v in o.data.vertices:v.co.y*=.31/.42
  o.location.y=-.335;o['rack_clearance']=True
 if o.name.startswith('PLK_Fridge_Inner_rack') and not o.get('rack_width_clearance'):
  for v in o.data.vertices:v.co.x*=.40/.47
  o['rack_width_clearance']=True
 if o.name.startswith('PLK_Fridge_Gasket') and not o.get('seal_front'):
  o.location.y+=.026;o['seal_front']=True
 if o.name in ['PLK_Fridge_Door','PLK_Fridge_Pull'] and not o.get('front_relief'):
  o.location.y+=.012;o['front_relief']=True
bpy.data.objects['PLK_Kettle_Lid_lift']['open_metres']=.035
for name in ['PLK_Serving_Drawer_0','PLK_Serving_Drawer_1']:bpy.data.objects[name].location.x=2.4
for idx in range(4):bpy.data.objects['PLK_Cup_'+str(idx)].location.z=1.03
# Small visible dispenser fittings and opaque sign backings.
def detail_box(name,parent,pos,size,mat):
 if bpy.data.objects.get(name):return
 bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name
 for c0 in list(o.users_collection):c0.objects.unlink(o)
 bpy.data.collections['PLK_Assets'].objects.link(o);o.parent=bpy.data.objects[parent];o.location=pos;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials[mat])
detail_box('PLK_Towel_slot','PLK_Hand_basin',(-.222,0,.525),(.014,.22,.018),'PLK_Bakelite_rubber')
detail_box('PLK_Towel_paper','PLK_Hand_basin',(-.21,0,.50),(.012,.17,.055),'PLK_Paper')
detail_box('PLK_Soap_lever','PLK_Hand_basin',(-.226,-.28,.14),(.035,.065,.018),'PLK_Bakelite_rubber')
detail_box('PLK_Handwash_sign_back','PLK_Hand_basin',(-.234,0,.405),(.018,.30,.07),'PLK_Bakelite_rubber')
detail_box('PLK_Dry_sign_back','PLK_Dry_store',(.525,-.003,1.845),(.92,.01,.12),'PLK_Bakelite_rubber')
detail_box('PLK_Cubby_Label_strip','PLK_Lost_property',(.25,-.006,.506),(.464,.012,.07),'PL03_Aged_Pine')
# Camera now covers basin from inside the kitchen, not behind cabinets.
review=bpy.data.collections['PLK_REVIEW_ONLY']
def camera(n,pos,tar,lens=28):
 o=bpy.data.objects.get('PLK_REVIEW_'+n)
 if o is None:
  d=bpy.data.cameras.new('PLK_REVIEW_'+n);o=bpy.data.objects.new(d.name,d);review.objects.link(o)
 o.location=(pos[0]-24.1,4-pos[1],4+pos[2]);target=Vector((tar[0]-24.1,4-tar[1],4+tar[2]));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.03;return o
camera('01_Customer',(2.5,7.5,1.65),(2.5,11.1,1.37),30)
camera('05_Washing',(1.72,14.08,1.65),(.45,14.58,.9),26)
camera('07_Handwashing',(3.24,13.98,1.65),(4.48,13.24,1.0),28)
cam=camera('06_Overhead',(2.5,13.5,8.5),(2.5,13.5,0));cam.data.type='ORTHO';cam.data.ortho_scale=7.8
camera('09_Cubby',(4.55,9.4,1.65),(4.32,10.95,.95),32)
camera('10_Beverage_equipment',(1.6,12.55,1.65),(.55,12.68,1.15),32)
camera('08_Open_mechanisms',(2.7,13.52,1.65),(1.7,15.35,.96),25)
# Face-mounted hinges and handed paired leaves: preserve every closed leaf position.
for piv in list(bpy.data.collections['PLK_Assets'].all_objects):
 if piv.get('motion')!='hinge' or piv.name.startswith(('PLK_Fridge','PLK_Microwave')):continue
 if not piv.get('final_pivot'):
  door=next(o for o in piv.children if '_Door_' in o.name and o.type=='MESH')
  dx=door.dimensions.x if '_Door_1_' in piv.name else 0
  piv.location.x+=dx;piv.location.y+=.030
  for ch in piv.children:
   ch.location.x-=dx;ch.location.y-=.030
   if 'Hinge_barrel' in ch.name:ch.location.x=0;ch.location.y=0
  piv['final_pivot']=True
 piv['open_degrees']=-90 if '_Door_1_' in piv.name else 90
piv=bpy.data.objects['PLK_Fridge_Door_Pivot']
if not piv.get('final_pivot'):
 delta=Vector((-.016,.045,0));piv.location+=delta
 for ch in piv.children:ch.location-=delta
 piv['final_pivot']=True
piv['open_degrees']=95
for o in bpy.data.collections['PLK_Assets'].all_objects:
 if o.name.startswith('PLK_Fridge_Shelf') and 'support' not in o.name:
  if not o.get('rack_clearance'):
   for v in o.data.vertices:v.co.y*=.34/.43
   o.location.y=-.32;o['rack_clearance']=True
for name in ['PLK_Fridge_Door_Pivot','PLK_Microwave_Door_Pivot','PLK_Rear_left_Door_0_Pivot']:
 o=bpy.data.objects[name]
 for f,angle in [(1,0),(40,o['open_degrees'])]:o.rotation_euler.z=math.radians(angle);o.keyframe_insert(data_path='rotation_euler',frame=f)
o=bpy.data.objects['PLK_Prep_drawers_Drawer_slide_1']
for f,y in [(1,0),(40,.38)]:o.location.y=y;o.keyframe_insert(data_path='location',frame=f)
s.frame_set(1);s.frame_end=40
# Clearances visualized only in the overhead review, excluded from assets/export.
c=bpy.data.collections.get('PLK_REVIEW_Access')
if c is None:c=bpy.data.collections.new('PLK_REVIEW_Access');s.collection.children.link(c)
for old in list(c.objects):bpy.data.objects.remove(old,do_unlink=True)
c.hide_render=True;c['export']=False
m=bpy.data.materials.get('PLK_REVIEW_Access_green') or bpy.data.materials.new('PLK_REVIEW_Access_green');m.diffuse_color=(.1,.65,.3,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.1,.65,.3,1)
def line(n,pts,r=.012):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,(x,d,z) in zip(sp.points,pts):p.co=(x-24.1,4-d,4+z,1)
 o=bpy.data.objects.new(n,cu);c.objects.link(o);cu.materials.append(m)
line('REVIEW_600mm_corridor',[(4.8,14.2,.032),(2.4,14.2,.032),(2.4,12.05,.032),(1.8,12.05,.032),(1.8,14.8,.032),(4.8,14.8,.032)])
line('REVIEW_Door_reserve',[(3.70,13.72,.035),(4.82,13.72,.035),(4.82,15.04,.035),(3.70,15.04,.035),(3.70,13.72,.035)],.008)
cu=bpy.data.curves.new('REVIEW_Access_caption','FONT');cu.body='600 mm STAFF PATH\nBLENDER CLEARANCE REVIEW';cu.size=.12;o=bpy.data.objects.new(cu.name,cu);c.objects.link(o);o.location=(-21.47,-9.2,4.045);cu.materials.append(m)
s.camera=bpy.data.objects['PLK_REVIEW_03_Staff_entry'];bpy.context.view_layer.update()
# Refresh authoritative closed-pose inventory after relocation.
p=OUT/'replacement_manifest.json';doc=json.loads(p.read_text());records=[]
for o in bpy.data.collections['PLK_Assets'].all_objects:
 records.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'dimensions':list(o.dimensions),'matrix_world':[list(r) for r in o.matrix_world],'location_parent':list(o.location),'rotation_parent_radians':list(o.rotation_euler),'materials':[m.name for m in o.data.materials] if o.type in {'MESH','FONT'} else [],'motion':dict(o.items()) if o.get('motion') else None})
doc['objects']=records;doc['layout_changes']=['Hand basin relocated from west rear corner to local (4.46,depth13.24,z0.86), yaw 180 degrees, so its standing area does not overlap rear cabinetry.','Waste bin moved to (4.48,depth12.62), clear of staff door and handwash approach.','West cabinet run ends at depth14.95; old hand basin segment is removed.','Fridge bay x2.20-2.96 is open under the rear top.','Serving drawers occupy x1.0-1.6, away from dry-store shelf; the public counter footprint is unchanged.']
doc['reference_export_exclusions']=['REFERENCE_ONLY_Source_Context','PLK_REVIEW_ONLY','PLK_REVIEW_Access'];doc['poses']={'closed':1,'representative_open':40};doc['views']=[{'name':o.name,'position_world':list(o.location),'rotation_radians':list(o.rotation_euler),'lens_mm':o.data.lens,'orthographic_scale':o.data.ortho_scale if o.data.type=='ORTHO' else None} for o in review.objects if o.type=='CAMERA'];p.write_text(json.dumps(doc,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Kitchen.blend'))
bpy.data.libraries.write(str(OUT/'PLK_Assets.blend'),{bpy.data.collections['PLK_Assets']},fake_user=True)
print('PLK REFINEMENT SAVED')
