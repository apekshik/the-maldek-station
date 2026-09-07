"""Retain the forest approach, replace only its final bend to meet the VF07 south landing access."""
import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();manifest=json.loads((OUT/'handoff_manifest.json').read_text());inventory=json.loads((OUT/'replacement_inventory.json').read_text())
old_path=json.loads((OUT.parent/'revision10/approach_path.json').read_text())['points']
with bpy.data.libraries.load(str(OUT.parent/'revision10/canyon_approach.blend'),link=False) as (src,dst):
 assert 'SM_R10_Forest_Approach' in src.objects;dst.objects=['SM_R10_Forest_Approach']
old=dst.objects[0];assert len(old.data.vertices)==2*len(old_path)
cut=max(i for i,p in enumerate(old_path) if p[1]<=-21.5)
start=Vector(old_path[cut]);end=Vector((-13.5,-19.5,0));tangent=(start-Vector(old_path[cut-1])).normalized();d=(end-start).length
c1=start+tangent*d*.4;c2=end-Vector((0,d*.3,0))
path=old_path[:cut+1]
for i in range(1,13):
 t=i/12;path.append(list((1-t)**3*start+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end))
vs=[tuple(old.data.vertices[i].co) for i in range(2*(cut+1))]
for i in range(cut+1,len(path)):
 p=Vector(path[i]);t=(i-cut)/12
 tangent=(p-Vector(path[i-1])) if i==len(path)-1 else Vector(path[i+1])-Vector(path[i-1]);length=math.hypot(tangent.x,tangent.y)
 half=1.25+(.6-1.25)*(t*t*(3-2*t))
 for s in [-1,1]:vs.append((p.x-s*tangent.y/length*half,p.y+s*tangent.x/length*half,p.z))
faces=[(2*i-2,2*i,2*i+1,2*i-1) for i in range(1,len(path))]
me=bpy.data.meshes.new('R12_Forest_Approach_Aligned');me.from_pydata(vs,[],faces);me.update();me.materials.append(bpy.data.materials['Ground'])
uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 for li in poly.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
o=bpy.data.objects.new('R12_Forest_Approach_Aligned',me);source.collection.objects.link(o);o['handoff_preserve_uv']=True;bpy.context.view_layer.update()
assert all((old.data.vertices[i].co-me.vertices[i].co).length<.000001 for i in range(2*(cut+1)))
target=next(r for r in inventory if r['label']=='R10_Forest_Approach');comp=target['components'][0]
h=Handoff(source,bpy.context.evaluated_depsgraph_get(),'fbx')
row=h.chunk('SM_R12_Forest_Approach_Aligned',[o],role='floor',surface='Gravel',targets=[{'actor':target['r12_path'],'component':comp['name'],'old_mesh':comp['mesh']}],exposure='Exterior')
row.update(stage='Circulation',collection='R12_Forest_Arrival_Junction',material_bindings_override={s:comp['materials'][0] for s in row['material_slots']})
manifest['chunks']=[r for r in manifest['chunks'] if r['name']!=row['name']]+[row];manifest['materials'].update(h.materials)
(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2));h.save('forest_arrival_export')
(OUT/'forest_arrival_alignment.json').write_text(json.dumps({'path':path,'preserved_cross_sections':cut+1,'preserved_vertices':2*(cut+1),'first_changed_station_coordinate':old_path[cut+1],'old_endpoint':old_path[-1],'new_endpoint':list(end),'existing_uvs_preserved':True,'old_material':comp['materials'][0],'reason':'Old final bend met east landing guard. Connect to approved south access without changing the forest route outside its final bend.'},indent=2))
print('FOREST_JUNCTION_EXPORTED',row['name'],cut+1,len(path),flush=True)
