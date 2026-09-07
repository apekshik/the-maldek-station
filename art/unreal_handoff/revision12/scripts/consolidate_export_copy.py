"""Assemble the reviewed mesh and collision patches into one final Blender export copy."""
import bpy,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];manifest=json.loads((base/'handoff_manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(base/'handoff_manifest.blend'),load_ui=False);scene=bpy.context.scene
changes=json.loads((base/'collision_refinement.json').read_text())['changed']
patches=[('parking_split_export.blend',[r['name'] for r in manifest['chunks'] if r.get('retained_from_combined')]),('collision_refinement_export.blend',[r['name'] for r in changes])]
for file,names in patches:
 def included(n):return n in names or any(n.startswith('UCX_'+name+'_') for name in names)
 for o in list(scene.objects):
  if included(o.name):bpy.data.objects.remove(o,do_unlink=True)
 with bpy.data.libraries.load(str(base/file),link=False) as (src,dst):dst.objects=[n for n in src.objects if included(n)]
 for o in dst.objects:
  if not o:continue
  scene.collection.objects.link(o)
  if o.type=='MESH':
   for i,m in enumerate(o.data.materials):
    if m and m.name.rsplit('.',1)[-1].isdigit():
     canonical=bpy.data.materials.get(m.name.rsplit('.',1)[0])
     if canonical:o.data.materials[i]=canonical
for r in manifest['chunks']:
 o=scene.objects.get(r['name']);assert o,r['name']
 assert [m.name for m in o.data.materials]==r['material_slots'],r['name']
 assert len([c for c in scene.objects if c.name.startswith('UCX_'+r['name']+'_')])==r['collision_hulls'],r['name']
bpy.ops.wm.save_as_mainfile(filepath=str(base/'VF07_R12_Export.blend'),copy=True)
print('CONSOLIDATED_EXPORT_COPY',len(manifest['chunks']),flush=True)
