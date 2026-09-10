"""Six new assemblies; immutable lodge 04 source. Blender 5.0.1."""
import bpy,json,math,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];SOURCE=Path(os.environ.get('MALDEK_SOURCE','C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'));HASH=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert HASH=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['Lodge_Integrated'];bpy.context.window.scene=s;s.frame_set(1)
for scene in list(bpy.data.scenes):
 if scene!=s:bpy.data.scenes.remove(scene)
s.name='PLG2_Fitted_Review';ref=bpy.data.collections.new('PLG2_REFERENCE_ONLY');s.collection.children.link(ref)
for c in list(s.collection.children):
 if c!=ref:s.collection.children.unlink(c);ref.children.link(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o);ref.objects.link(o)
ref['exclude_from_delivery']=True
col=bpy.data.collections.new('PLG2_East_Wall_Details');s.collection.children.link(col);roots=[];layers=[];textures={}
# Load helper definitions with frame defaults resolved to existing source pine.
pine=bpy.data.materials.get('PL03_Aged_Pine');assert pine
exec(compile((P/'scripts/mesh_helpers.py').read_text(),str(P/'scripts/mesh_helpers.py'),'exec'))
metal=material('Petrol_enamel',(.04,.095,.10),.45,.40);cream=material('Cream_enamel',(.63,.60,.47),.18,.42);steel=material('Galvanized',(.32,.35,.33),.80,.32);paper=material('Paper_edges',(.72,.68,.56),0,.88);rubber=material('Dark_seals',(.022,.029,.026),0,.8);glass=material('Modest_glass',(.98,.98,.98),0,.065);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45;dust=material('Ledge_dust',(.26,.23,.17),0,1)
# Two elevated illustrations form one staggered group, but retain separate roots.
framed('Safety',(-10.300,-1.12,5.78),(0,-1,0),.70,.95,'safety',pine)
framed('Archive_A',(-10.300,-2.10,6.10),(0,-1,0),.55,.40,'archive_1',metal)
framed('Archive_B',(-10.300,-2.40,5.46),(0,-1,0),.55,.40,'archive_2',pine)
# Small caption plates stand free of paper and rails on the lower print margin.
for name in ['Archive_A','Archive_B']:
 r=bpy.data.objects['PLG2_'+name]
 box(name+'_caption_plate',r,(0,-.144,.0268),(.47,.046,.0012),cream,.0002)
 face(name+'_caption_art',r,.464,.04,.0277,'caption_'+name[-1],.0003).location.y=-.144
 for x in [-.21,.21]:screw(name+'_caption_fix',r,x,-.144,.029)
# Shallow six-pocket leaflet rack; stand-offs clear the existing dado.
r=root('Leaflet_rack',(-10.322,-3.23,5.18),(0,-1,0));r['display_size_m']=[.45,.60];r['max_wall_projection_m']=.16
box('Rack_back',r,(0,0,.003),(.45,.60,.006),metal,.001)
for x in [-.18,.18]:
 for y in [-.235,.24]:
  box('Rack_standoff',r,(x,y,-.018),(.028,.038,.032),steel,.001);screw('Rack_wall_fix',r,x,y,.009)
for x in [-.222,.222]:box('Rack_return',r,(x,0,.055),(.006,.60,.104),metal,.001)
face('Rack_heading',r,.39,.04,.010,'rack_label',.0005).location.y=.272
counts=[[2,6],[0,3],[4,1]]
for row,base in enumerate([.038,-.137,-.285]):
 for j,x in enumerate([-.109,.109]):
  box('Pocket_floor',r,(x,base,.056),(.209,.003,.101),metal,.0006)
  box('Pocket_front_lip',r,(x,base+.040,.105),(.207,.078,.004),cream,.0008)
  # Rolled top lip catches light; closed cylinder axis X.
  rim=cyl('Pocket_rolled_edge',r,(x,base+.080,.105),.003,.207,metal);rim.rotation_euler.y=math.pi/2
  for k in range(counts[row][j]):
   # Real paper shells with unequal depths, folded panel ridges and uneven top edges.
   art=['routes','lodge','care'][(row+j)%3];leaf=face(f'Leaflet_{row}_{j}_{k}',r,.17,.205,.028+k*.0022,'leaflet_'+art,.00035,curl=.00001)
   leaf.location=(x+(k%3-1)*.002,base+.106+(k%2)*.003,0)
   for v in leaf.data.vertices:
    # Tri-fold crease profile, retained as physical geometry at quarter-millimetre scale.
    xx=(v.co.x+.085)/.17;v.co.z+=.0007*abs(math.sin(xx*math.pi*3))
   leaf['folds']='three-panel folded leaflet; closed stack';leaf.rotation_euler.x=math.radians(-4+k*.45)
r['stack_counts']=str(counts)
# Analog thermometer/hygrometer: two separate instrument faces, needles and thin glazing.
r=root('Climate_gauge',(-10.300,-4.03,5.91),(0,-1,0));r['display_size_m']=[.22,.35]
box('Gauge_housing',r,(0,0,.023),(.22,.35,.042),pine,.01)
for y,kind,angle in [(.081,'temperature',-50),(-.081,'humidity',0)]:
 cyl('Gauge_'+kind+'_rim',r,(0,y,.049),.077,.012,steel)
 dial=cyl('Gauge_'+kind+'_dial',r,(0,y,.056),.070,.002,paper);dial.data.materials.append(tex('gauge_'+kind));uv=dial.data.uv_layers.active
 for poly in dial.data.polygons:
  if poly.normal.z>.5:
   poly.material_index=1
   for li in poly.loop_indices:
    co=dial.data.vertices[dial.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x/.14+.5,co.y/.14+.5)
 pivot=bpy.data.objects.new('PLG2_'+kind+'_NeedlePivot',None);col.objects.link(pivot);pivot.parent=r;pivot.location=(0,y-.0049,.060);pivot.rotation_euler.z=math.radians(angle)
 box('Gauge_'+kind+'_needle',pivot,(0,.023,0),(.0018,.051,.0015),rubber,.0003);cyl('Gauge_'+kind+'_axle',r,(0,y-.0049,.062),.0038,.005,steel)
 cyl('Gauge_'+kind+'_glass',r,(0,y,.067),.070,.0015,glass)
for y in [-.158,.158]:screw('Gauge_mount',r,.091,y,.047)
r['static_readings']='Approx. 18 C / 50 percent RH. Decorative, no live weather logic.'
# First-aid cabinet: open shell, folded returns, separately hinged empty leaf.
r=root('First_aid',(-10.300,-5.02,5.61),(0,-1,0));r['display_size_m']=[.38,.45];r['depth_m']=.14
box('Cabinet_back',r,(0,0,.006),(.38,.45,.006),cream,.001)
for x in [-.187,.187]:box('Cabinet_side_return',r,(x,0,.064),(.006,.45,.11),cream,.001)
for y in [-.222,.222]:box('Cabinet_top_bottom_return',r,(0,y,.064),(.368,.006,.11),cream,.001)
# Stop strips are recessed behind the leaf, never crossing the hinge path.
for x in [-.17,.17]:box('Cabinet_stop',r,(x,0,.116),(.014,.405,.003),rubber,.0005)
for x in [-.14,.14]:
 for y in [-.18,.18]:
  box('Cabinet_mount_tab',r,(x,y,-.005),(.035,.06,.014),steel,.001);screw('Cabinet_back_fix',r,x,y,.011)
hinge=bpy.data.objects.new('PLG2_Cabinet_LeafPivot',None);col.objects.link(hinge);hinge.parent=r;hinge.location=(-.184,0,.131);hinge['open_angle_degrees']=-95.;hinge['axis']='local Y; world +Z';hinge['purpose']='future hinge pivot, no gameplay'
leaf=box('Cabinet_leaf',hinge,(.184,0,0),(.368,.436,.009),cream,.002)
printob=face('Cabinet_label',hinge,.31,.35,.0055,'first_aid',.0004);printob.location.x=.184
# Piano-style alternating fixed and moving knuckles on the outside of the hinge.
for y in [-.15,.15]:
 cyl('Cabinet_hinge_pin',r,(-.184,y,.131),.003,.062,steel,'Y')
 for k in range(3):
  parent=hinge if k==1 else r;xx=0 if k==1 else -.184;zz=0 if k==1 else .131
  cyl('Cabinet_hinge_knuckle',parent,(xx,y+(k-1)*.018,zz),.006,.016,steel,'Y')
 box('Cabinet_hinge_fixed_tab',r,(-.175,y,.121),(.028,.055,.004),steel,.001)
# Latch is a separate simple turn tab, no lock/key/contents.
latch=cyl('Cabinet_latch_axle',hinge,(.323,0,.009),.007,.012,steel)
box('Cabinet_turn_latch',hinge,(.323,0,.017),(.027,.010,.007),metal,.002)
for frame,angle in [(1,0),(40,-95)]:hinge.rotation_euler.y=math.radians(angle);hinge.keyframe_insert(data_path='rotation_euler',index=1,frame=frame)
s.frame_set(1)
# Controlled handling marks, tiny ledge dust, one small off-square frame.
for r in roots:
 if r.name in ['PLG2_Safety','PLG2_Archive_A','PLG2_Archive_B']:
  w,h=r['display_size_m'];box(r.name+'_top_dust',r,(0,h/2+.0002,.024),(w*.64,.0003,.014),dust)
  for i in range(3):box(r.name+'_rubbed_edge',r,(w/2-.012,-h*.27+i*h*.24,.0372),(.0015,.009,.0003),paper)
# Settled dust in depleted rack pocket; small rubbed paint at cabinet latch edge.
rr=bpy.data.objects['PLG2_Leaflet_rack'];box('Empty_pocket_dust',rr,(-.109,-.135,.063),(.13,.0005,.055),dust)
for j in range(4):
 box('Cabinet_latch_wear',hinge,(.350,-.022+j*.014,.0048),(.0012,.004+j*.001,.0003),steel)
# Roughness variation limited to painted materials, editable and Blender-only.
for m in [metal,cream]:
 nt=m.node_tree;pr=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=47
 ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=.35;ramp.inputs['To Max'].default_value=.57;nt.links.new(noise.outputs['Fac'],ramp.inputs['Value']);nt.links.new(ramp.outputs['Result'],pr.inputs['Roughness'])
bpy.context.view_layer.update()
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
manifest=dict(source=str(SOURCE),source_sha256=HASH,collection=col.name,replace=[],wall_patches=[],units='metres, Z up; floor Z=4',assembly_axes='Local X toward -Y, local Y up +Z, local Z outward -X; root matrices are source-scene assembly transforms.',roots=[r.name for r in roots],objects=[dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,matrix_world=[list(row) for row in o.matrix_world],dimensions=list(o.dimensions),bounds=bounds(o) if o.type=='MESH' else None,materials=[m.name for m in o.data.materials] if o.type=='MESH' else [],artwork=o.get('artwork')) for o in col.objects],surface_layers=layers,poses={'closed':1,'cabinet_open':40},cabinet_pivot={'name':hinge.name,'local_position':list(hinge.location),'axis':'local Y / world Z','sweep_degrees':[0,-95]},trim='Rack stand-offs bridge dado without modification; back surface X=-10.322 gives >=30 mm to rail front X=-10.292.',reserved_band='New rectangles total 1.623 m2. Cluster bounding display band Y -5.21 to -0.77, Z 4.88 to 6.30 is 6.305 m2: 25.7 percent filled. Kept toward sparse end to preserve separate map and locker groups.',reference_exclusions=['PLG2_REFERENCE_ONLY','PLG2_REVIEW_ONLY'],editorial=['Archival pictures are original monochrome illustrative studies, not documentary photographs. No canonical date/event asserted.','Mountain-care copy is advisory dressing, not a gameplay rule.','Gauge is static approx.18 C /50% RH.','No added cabinet contents, keys, collectibles or interactions.'],materials='Reused pine from integrated source and new procedural roughness require bake for engine. Flat print textures are packed with editable SVG originals.')
(P/'placement_manifest.json').write_text(json.dumps(manifest,indent=2))
# Fitted copy retains all integrated state and source geometry. Delivery excludes it entirely.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_East_Wall_Details_Fitted.blend'))
deliver=bpy.data.scenes.new('PLG2_Delivery');deliver.collection.children.link(col);deliver.unit_settings.system='METRIC';deliver.frame_end=40;bpy.context.window.scene=deliver;bpy.data.scenes.remove(s)
keep=set(col.objects)
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c!=col:bpy.data.collections.remove(c)
bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_East_Wall_Details.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==HASH
print('BUILT',len(roots),'assemblies',len(col.objects),'objects')
