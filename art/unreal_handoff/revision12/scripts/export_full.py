"""Explicit VF07 assembly handoff; forest-relative terrain delta; original source never saved."""
import sys,math,json,bisect
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();h=Handoff(source,deps,'fbx')
inventory=json.loads((OUT/'replacement_inventory.json').read_text());actors={r['label']:r for r in inventory}
# This table is the entire architectural replacement boundary. Unlisted actors are retained.
mapping={
 '01_Upper_Platform':('Infrastructure','R04_01_Upper_Platform'),
 '04_Lower_Drive':('Architecture','R04_04_Lower_Drive'),
 '05_Generator_Room':('Architecture','R04_05_Generator_Room'),
 '06_Stairs_and_Landings':('Circulation','R04_06_Stairs_and_Landings'),
 '09_Relay_and_Paths':('Architecture','R04_09_Relay_and_Paths'),
 '12_Gondola':('Infrastructure','R04_12_Gondola'),
 '13_Roofs':('Architecture','R04_13_Roofs'),
 '14_Site_Structure':('Circulation','R04_14_Site_Structure'),
 '18_Cliff_Anchors':('Infrastructure','R04_18_Cliff_Anchors'),
 '20_Lookout_Bridge':('Infrastructure','R04_20_Lookout_Bridge'),
 '21_Maintenance':('Architecture','R04_21_Maintenance'),
 'VF06_Canopy_Junction':('Infrastructure','R04_01_Upper_Platform'),
 'VF06_Control':('Architecture','R04_02_Control_Room'),
 'VF06_Gondola_Details':('Infrastructure','R04_12_Gondola'),
 'VF06_Lower_Gallery_Details':('Architecture','R04_04_Lower_Drive'),
 'VF06_Maintenance_Shells':('Architecture','R04_21_Maintenance'),
 'VF06_Quarters':('Architecture',None),
 'VF06_Relay_Shell':('Architecture','R04_09_Relay_and_Paths'),
 'VF06_Service_Hardware':('Infrastructure',None),
 'VF06_Transferred_Details':('Infrastructure',None),
 'VF06_Waiting_Hall':('Architecture','R04_03_Waiting_Hall'),
 'VF06_Water_Service_Terrace':('Circulation',None),
 'VF06_Water_Tower':('Infrastructure',None),
 'VF07_Continuous_Service_Routes':('Circulation','R04_08_Fuel_Yard'),
 'VF07_Deck_Structure':('Circulation','R04_01_Upper_Platform'),
 'VF07_Internal_Tread_Refresh':('Circulation','R04_06_Stairs_and_Landings'),
 'VF07_Public_Deck':('Circulation','R04_01_Upper_Platform'),
 'VF07_Public_Guards':('Circulation','R04_01_Upper_Platform'),
 'VF07_Quarters_Access':('Circulation',None),
 'VF07_Service_Apron':('Circulation','R04_08_Fuel_Yard'),
 'VF07_Service_Descent':('Circulation','R04_06_Stairs_and_Landings'),
 'VF07_Sideways_Arrival':('Circulation','R04_06_Stairs_and_Landings'),
 'VF07_Water_Pipework':('Infrastructure',None),
}
rooms=[(-8,-2.2,-5.2,0,4,7.15),(-17.8,-8,-7.8,0,4,7.15),(-7.7,-1.4,-4.6,1.3,7.65,10.4),(-2,6,-6,0,0,3.4),(27,33,-19,-11,-1,2.2),(33,36,-18,-13,-1,2.2),(46,50,11,15,3,6)]
def exposure(o):
 a,b=bounds(o);x,y,z=[(a[i]+b[i])/2 for i in range(3)]
 for x0,x1,y0,y1,z0,z1 in rooms:
  if x0+.04<x<x1-.04 and y0+.04<y<y1-.04 and z0-.3<z<z1-.08:return 'Indoor'
 return 'Exterior'
def role(o):
 n=o.name.lower()
 if any(m and 'glass' in m.name.lower() for m in getattr(o.data,'materials',[])):return 'glass'
 if any(w in n for w in ['grating','tread']):return 'grating'
 if any(w in n for w in ['rail','guard','cable','wire','pipe','rung']):return 'thin'
 if o.type=='FONT':return 'signage'
 if collision_kind(o)=='floor':return 'floor'
 return 'solid'
def visible(o):return not o.hide_render and o.get('export_geometry',True) and o.type in {'MESH','CURVE','FONT'}
all_exported=[]
for collection,(stage,target) in mapping.items():
 assert collection in bpy.data.collections,collection
 if target:assert target in actors,target
 objects=list(bpy.data.collections[collection].objects);groups=defaultdict(list);guides=[]
 for o in objects:
  if not visible(o):
   if o.get('collision',False):guides.append(o)
   continue
  a,b=bounds(o);cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2;r=role(o)
  surf=physical(next((m.name for m in getattr(o.data,'materials',[]) if m),'Metal')) if r in ['floor','grating'] else 'Metal'
  groups[(math.floor(cx/8),math.floor(cy/8),r,surf,exposure(o))].append(o)
 for o in guides:
  a,b=bounds(o);center=Vector([(a[i]+b[i])/2 for i in range(3)])
  # Keep each authored proxy with the nearest visible assembly, never discard it.
  key=min(groups,key=lambda k:min((Vector([(bounds(v)[0][i]+bounds(v)[1][i])/2 for i in range(3)])-center).length_squared for v in groups[k]))
  groups[key].append(o)
 for index,(key,obs) in enumerate(sorted(groups.items())):
  gx,gy,r,surf,ex=key;pivot=(0,8.05,4) if target=='R04_12_Gondola' else (gx*8,gy*8,0)
  targets=[{'actor':actors[target]['r12_path'],'component':actors[target]['components'][0]['name'],'old_mesh':actors[target]['components'][0]['mesh']}] if target else []
  row=h.chunk(f'SM_R12_{slug(collection)}_{index:03d}_{r}',obs,pivot=pivot,role=r,surface=surf,targets=targets,exposure=ex)
  row.update(stage=stage,collection=collection,source_collision_guides=[o.name for o in obs if o.hide_render and o.get('collision',False)])
  all_exported+=row['sources']
# Parking/car and cable route remain exactly the existing Unreal assemblies/controller.
excluded={'10_Parking_and_Arrival':'Preserve current parking and approach assembly','19_Cable_Route':'Preserve Unreal controller and spline route','VF06_Presentation':'Blender presentation only','15_Terrain':'Replaced by the forest-relative delta below'}
for c in source.collection.children:
 if c.name not in mapping and c.name not in excluded:
  assert not any(visible(o) for o in c.all_objects),('Unmapped visible collection',c.name)

def grid(path):
 d=json.loads(path.read_text());vs=d['vertices'];xs=sorted(set(v[0] for v in vs));ys=sorted(set(v[1] for v in vs));zz={(v[0],v[1]):v[2] for v in vs}
 def sample(x,y):
  i=max(0,min(len(xs)-2,bisect.bisect_right(xs,x)-1));j=max(0,min(len(ys)-2,bisect.bisect_right(ys,y)-1));x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];u=(x-x0)/(x1-x0);v=(y-y0)/(y1-y0)
  return (1-v)*((1-u)*zz[x0,y0]+u*zz[x1,y0])+v*((1-u)*zz[x0,y1]+u*zz[x1,y1])
 return sample,xs,ys
forest,fx,fy=grid(OUT.parent/'forest_test/terrain_grid.json');old,_,_=grid(OUT.parent/'revision11/terrain_grid.json')
terrain=bpy.data.objects['R11_Current_Terrain'];a,b=bounds(terrain);vs=[];changes=[];outside_error=0
# Mask bounds encompass only approved VF06/07 local terrain edits, including their feather.
mask=[[-30,58],[-30,33]]
for vert in terrain.data.vertices:
 p=terrain.matrix_world@vert.co;x,y,z=p
 delta=z-old(x,y);inside=mask[0][0]<=x<=mask[0][1] and mask[1][0]<=y<=mask[1][1]
 if not inside:outside_error=max(outside_error,abs(delta));delta=0
 value=forest(x,y)+delta;vs.append((x,y,value))
 if abs(delta)>.001:changes.append([x,y,delta])
assert outside_error<.001,('VF07 terrain changes outside authorized mask',outside_error)
me=bpy.data.meshes.new('R12_Forest_Relative_Terrain');me.from_pydata(vs,[],[tuple(p.vertices) for p in terrain.data.polygons]);me.update()
for m in terrain.data.materials:me.materials.append(m)
ob=bpy.data.objects.new('R12_Forest_Relative_Terrain',me);source.collection.objects.link(ob);bpy.context.view_layer.update();h.deps=bpy.context.evaluated_depsgraph_get()
row=h.chunk('SM_R12_Terrain',[ob],role='terrain',surface='Soil',targets=[{'actor':actors['R04_Local_Terrain']['r12_path'],'component':actors['R04_Local_Terrain']['components'][0]['name'],'old_mesh':actors['R04_Local_Terrain']['components'][0]['mesh']}]);row.update(stage='Circulation',collection='15_Terrain',complex_collision=True,preserve_material=actors['R04_Local_Terrain']['components'][0]['materials'])
(OUT/'terrain_grid.json').write_text(json.dumps({'vertices':vs,'mask':mask,'changed_vertices':len(changes),'max_delta_m':max(abs(p[2]) for p in changes),'outside_mask_source_difference_m':outside_error}))
(OUT/'terrain_changes.json').write_text(json.dumps(changes))
manifest=h.save('handoff_manifest');manifest['excluded_collections']=excluded;manifest['terrain_mask']=mask
manifest['retire_components']=[{'actor':actors[n]['r12_path'],'component':actors[n]['components'][0]['name'],'old_mesh':actors[n]['components'][0]['mesh'],'reason':'Superseded by continuous VF07 deck / reviewed room shell'} for n in ['R04_07_Overlook','R04_11_Doors_Door_Control_Platform','R04_11_Doors_Door_Generator_Yard','R10_Hall_Foundation_0','R10_Hall_Foundation_1','R10_Hall_Foundation_2']]
(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2))
print('FULL_EXPORT_COMPLETE',len(h.chunks),len(all_exported),len(h.materials),flush=True)
