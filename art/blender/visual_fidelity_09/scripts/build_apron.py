"""VF09: coherent concrete apron and matching open-grating perimeter."""
import bpy,math,ast,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'visual_fidelity_08/Maldek_Generator_Fuel_Refinement.blend'));s=bpy.context.scene
steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized'];blue=bpy.data.materials['VF06_Petrol_paint'];concrete=bpy.data.materials['VF06_Concrete'];cream=bpy.data.materials['VF06_Warm_enamel'];rust=bpy.data.materials['VF06_Fastener_oxidation'];deck_rects=[]
for rel,names in [('visual_fidelity_01/scripts/build_sample.py',['mesh','box','beam','bolt','camera','area']),('visual_fidelity_02/scripts/build_redesign.py',['cylinder']),('visual_fidelity_06/scripts/build_integrated.py',['bounds','col','pipe','rail','deck_rect'])]:
 for n in ast.parse((OUT.parent/rel).read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module(body=[n],type_ignores=[]),rel,'exec'))
# Preserve geometry of approved plant, tank, room and water tower assemblies.
preserved={o.name:[list(v) for v in bounds(o)] for c in bpy.data.collections if c.name in ['VF08_04_Diesel_Generator','VF08_06_Diesel_Tank','VF06_Water_Tower'] for o in c.objects if o.type=='MESH'}
removed=[]
for cn in ['VF06_Water_Service_Terrace','VF08_08_Site_Transitions']:
 for o in list(bpy.data.collections[cn].objects):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 if o.name.startswith('VF08_Fill_access_pad') or (o.name.startswith('Service_road') and o.type=='MESH'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Foundation cores stop at facades, leaving a real open trench beneath border grating.
o=bpy.data.objects['VF08_Hall_foundation'];o.scale.x*=10/10.2;o.scale.y*=10/10.2
# Named rectangles share boundaries; concrete never backs open grating.
group=col('VF09_01_Concrete_Apron');apron=group
concrete_rects=[(18.8,23.2,-20.2,-16),(24.2,26.2,-25.3,-12.4),(26.2,27,-24,-22.1),(27,37,-20.15,-19.35)]
for k,(a,b,c,d) in enumerate(concrete_rects):
 nx=max(1,round((b-a)/2));ny=max(1,round((d-c)/2))
 for i in range(nx):
  for j in range(ny):
   x0=a+(b-a)*i/nx;x1=a+(b-a)*(i+1)/nx;y0=c+(d-c)*j/ny;y1=c+(d-c)*(j+1)/ny
   box('VF09_Concrete_panel',((x0+x1)/2,(y0+y1)/2,-1.14),(x1-x0-.006,y1-y0-.006,.28),concrete,.004)
 # Coherent recessed foundation stem under each slab, rather than exposed small feet.
 box('VF09_Recessed_plinth',((a+b)/2,(c+d)/2,-1.55),(b-a-.10,d-c-.10,.55),concrete,.006)
group=col('VF09_02_Open_Grating');grates=group
grate_rects=[(17.8,18.8,-21.2,-15),(23.2,24.2,-21.2,-15),(18.8,23.2,-21.2,-20.2),(18.8,23.2,-16,-15),(26.2,27,-22.1,-12.4),(26.2,27,-25.3,-24),(27,37,-19.35,-19)]
for r in grate_rects:deck_rect(*r,-1,'grate')
for o in grates.objects:o.name='VF09_'+o.name
# Continuous building and bund stem foundations conceal the old scattered feet.
group=apron
box('VF09_Hall_stem_foundation',(32,-14,-1.73),(9.98,9.98,.64),concrete,.006)
box('VF09_Workshop_stem_foundation',(39,-15,-1.63),(3.98,5.98,.55),concrete,.006)
box('VF09_Bund_stem_foundation',(32,-22.7,-1.70),(9.98,5.08,.44),concrete,.006)
# Straight, grounded support beams unify the visible apron perimeter.
group=col('VF09_03_Perimeter_Structure');structure=group
for x in [17.8,24.2]:box('VF09_Water_edge_beam',(x,-18.1,-1.18),(.12,6.2,.26),steel,.004)
for y in [-21.2,-15]:box('VF09_Water_edge_beam',(21,y,-1.18),(6.4,.12,.26),steel,.004)
for x in [18.05,23.95]:
 for y in [-20.95,-15.25]:
  box('VF09_Water_edge_support',(x,y,-1.56),(.35,.35,.55),steel,.004)
  box('VF09_Foundation_shoe',(x,y,-1.85),(.60,.60,.08),concrete,.006)
# Guard only exposed water-pad edges; east side has a clear 2 m link to the promenade.
for a,b in [((17.8,-21.2,-1),(24.2,-21.2,-1)),((17.8,-21.2,-1),(17.8,-15,-1)),((17.8,-15,-1),(24.2,-15,-1)),((24.2,-21.2,-1),(24.2,-19.2,-1)),((24.2,-17.2,-1),(24.2,-15,-1))]:rail(a,b)
# Service road now meets one broad level landing, without the obsolete diagonal grill.
group=col('VF09_04_Service_Approach');approach=group
pts=[Vector(v) for v in [(18,-9,0),(18,-10,-.1),(20,-11,-.4),(22,-12,-.7),(23.0,-12.8,-.9),(24.2,-13.8,-1)]]
vs=[]
for i,p in enumerate(pts):
 tangent=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];tangent.z=0;tangent.normalize();side=Vector((-tangent.y,tangent.x,0))
 vs.extend([p-side*1.05,p+side*1.05])
# Final cross section lies precisely on the straight apron edge x=24.2.
vs[-2]=Vector((24.2,-14.85,-1));vs[-1]=Vector((24.2,-12.75,-1))
o=mesh('VF09_Connected_service_road',vs,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(pts)-1)],concrete)
mod=o.modifiers.new('Continuous road thickness','SOLIDIFY');mod.thickness=.18;mod.offset=-1
# Replace only the long main pipe; retain the existing wall valve and brackets.
group=col('VF09_05_Water_Main');water=group
for o in list(bpy.data.collections['VF07_Water_Pipework'].objects):
 if o.name.startswith('Water_main'):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
waterpoints=[(21,-18,-.45),(21,-18,-1.5),(17.2,-18,-1.5),(17.2,-13.5,-1.5),(17.2,-12,-.45),(15,-10,-.45),(8,-10,-.45),(6.2,-8,-.45),(6.2,-5,-.45),(6.2,-5,1.3)]
for a,b in zip(waterpoints,waterpoints[1:]):pipe('VF09_Water_main',a,b,.065,blue)
# Lower underlay under grating, and blend the complete terrace footprint into terrain.
terrain=bpy.data.objects.get('R11_Current_Terrain');changed=0
if terrain:
 for v in terrain.data.vertices:
  p=terrain.matrix_world@v.co
  # Water terrace and apron perimeter, not a rectangular cut across the whole mountain.
  distances=[math.hypot(max(a-p.x,0,p.x-b),max(c-p.y,0,p.y-d)) for a,b,c,d in [(17.5,27.1,-25.5,-12.3),(27,37.1,-20.3,-19)]]
  dist=min(distances)
  if dist<1.5 and p.z>-1.86:
   p.z+=(min(p.z,-1.86)-p.z)*max(0,1-dist/1.5);v.co=terrain.matrix_world.inverted()@p;changed+=1
# Two further inspection cameras, alongside the inherited whole-yard view.
group=bpy.data.collections['VF08_90_Presentation'];stage=group
camera('06_Water_Connection',(12,-28,8),(22,-17.5,-.8),40)
camera('07_Apron_Plan',(26,-18,30),(26,-18,-1),44)
s.camera=bpy.data.objects['01_Generator_and_Fuel'];s.cycles.samples=24
bpy.context.view_layer.update()
(OUT/'layout.json').write_text(json.dumps({'removed_objects':removed,'concrete_rects':concrete_rects,'grate_rects':grate_rects,'floor_z':-1,'water_pipe':waterpoints,'approach_centerline':[list(p) for p in pts],'terrain_vertices_changed':changed,'preserved_bounds':preserved},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Service_Apron_Refinement.blend'))
print('VF09_SAVED',flush=True)
