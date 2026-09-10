"""Deterministic post-assembly repairs; run after integrate.py."""
import bpy,bmesh,json
from mathutils import Matrix,Vector
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];f=OUT/'Maldek_Passenger_Lodge_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;s.frame_set(1)
o=s.objects['PL03_Grate_PL02_Deck_029_3_0']
# A whole-panel boolean welded two touching bars into a four-face edge away
# from the threshold. Replay the cut per original disconnected bar instead.
with bpy.data.libraries.load(str(OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'),link=False) as (a,b):b.objects=[o.name]
original=b.objects[0];me=original.data
adj={v.index:set() for v in me.vertices}
for e in me.edges:
 a,b=e.vertices;adj[a].add(b);adj[b].add(a)
remaining=set(adj);parts=[]
while remaining:
 todo=[remaining.pop()];component=set(todo)
 while todo:
  for n in adj[todo.pop()]:
   if n in remaining:remaining.remove(n);component.add(n);todo.append(n)
 parts.append(component)
patches=[p for p in json.loads((OUT.parent/'passenger_lodge_doors_01/wall_patches.json').read_text())['patches'] if p['source_object']==o.name]
verts=[];faces=[];cut_parts=0
for component in parts:
 ids=sorted(component);mapping={j:i for i,j in enumerate(ids)}
 mesh=bpy.data.meshes.new('PLI_bar');mesh.from_pydata([me.vertices[j].co for j in ids],[],[[mapping[j] for j in p.vertices] for p in me.polygons if p.vertices[0] in component]);mesh.update()
 ob=bpy.data.objects.new('PLI_TEMP_bar',mesh);s.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy()
 for p in patches:
  T=Matrix(p['matrix_world']);ctr=Vector(p['local_box_center']);dim=Vector(p['local_box_dimensions'])
  ps=[T.inverted()@ob.matrix_world@Vector(v) for v in ob.bound_box]
  if not all(max(v[i] for v in ps)>ctr[i]-dim[i]/2 and min(v[i] for v in ps)<ctr[i]+dim[i]/2 for i in range(3)):continue
  bpy.ops.mesh.primitive_cube_add(size=1);tool=bpy.context.object;tool.matrix_world=T@Matrix.Translation(ctr)@Matrix.Diagonal(Vector((*dim,1)))
  mod=ob.modifiers.new('Threshold_cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
  bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True);cut_parts+=1
 start=len(verts);verts.extend([v.co.copy() for v in ob.data.vertices]);faces.extend([[j+start for j in p.vertices] for p in ob.data.polygons]);bpy.data.objects.remove(ob,do_unlink=True)
new=bpy.data.meshes.new(o.name+'_barwise_threshold');new.from_pydata(verts,[],faces);new.update()
for m in o.data.materials:new.materials.append(m)
o.data=new;bpy.data.objects.remove(original,do_unlink=True)
bm=bmesh.new();bm.from_mesh(new);assert all(e.is_manifold for e in bm.edges);bm.free()
r=json.loads((OUT/'reconciliation.json').read_text());r['threshold_topology_repair']={'object':o.name,'operation':'Replay threshold cut per disconnected original bar, avoiding boolean welding at an unrelated touching edge','original_bars':len(parts),'cut_bars':cut_parts}
(OUT/'reconciliation.json').write_text(json.dumps(r,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(f),compress=True)
