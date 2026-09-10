"""Rebuild the integrated lodge from immutable delivery libraries; Blender 5.0."""
import bpy, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]; ART=OUT.parent
OUT.mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
specs=[
 ('windows','Maldek_Passenger_Lodge_Windows.blend','PLW_Assets','replace'),
 ('doors','Maldek_Passenger_Lodge_Doors.blend','PLD_ASSETS','replaced_proxies'),
 ('restrooms','Maldek_Passenger_Lodge_Restrooms.blend','PLR_Assets','replacements'),
 ('kitchen','weathering/PLK_Assets_Weathered.blend','PLK_Assets','replacements'),
 ('seating','Maldek_Passenger_Lodge_Seating.blend','PLS_Seating_Kit','replacement_objects'),
 ('lockers','PLL_Asset_Only.blend','PLL_Lockers','replaced'),
 ('wall_details','Maldek_Passenger_Lodge_Wall_Details.blend','PLG_Wall_Details','retire_exact')]
source=ART/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
shell=ART/'passenger_lodge_shell_01/Maldek_Lodge_Shell_Polish.blend'
expected='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796'
assert sha(source)==expected
report={'source_sha256':expected,'shell_sha256':sha(shell),'packages':[], 'retired':[], 'trim_repairs':[]}
bpy.ops.wm.open_mainfile(filepath=str(shell));s=bpy.data.scenes['Shell_Polish_Review'];bpy.context.window.scene=s;s.name='Lodge_Integrated'
s.frame_set(1)
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def signature(o):
 return {'matrix':[list(r) for r in o.matrix_world], 'bounds':bounds(o) if o.type=='MESH' else None}
baseline={o.name:signature(o) for o in s.objects}
def retire(name):
 if name in report['retired']:return
 o=s.objects.get(name)
 assert o is not None, 'Missing replacement: '+name
 # Unlink only from the integrated scene's collections, preserving other source scenes.
 for c in list(o.users_collection):c.objects.unlink(o)
 report['retired'].append(name)
for kind,file,collection,key in specs:
 folder=ART/f'passenger_lodge_{kind}_01';manifest=read(folder/'replacement_manifest.json')
 assert manifest['source_sha256']==expected
 names=manifest[key]
 if isinstance(names,dict):names=list(names)
 names=[x['name'] if isinstance(x,dict) else x for x in names]
 for name in names:retire(name)
 with bpy.data.libraries.load(str(folder/file),link=False) as (src,dst):
  assert collection in src.collections,collection
  dst.collections=[collection]
 c=dst.collections[0];s.collection.children.link(c)
 bpy.context.view_layer.update()
 report['packages'].append({'kind':kind,'file':str((folder/file).relative_to(ART)), 'sha256':sha(folder/file),'collection':c.name,'objects':{o.name:signature(o) for o in c.all_objects}})
 print('APPENDED',kind,len(c.all_objects),flush=True)
for name in ['PLK_Menu_Editable','PLK_Cubby_Label']:retire(name)
def load_module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
report['door_patch_count']=load_module(ART/'passenger_lodge_doors_01/scripts/apply_opening_patches.py','pld_patch').apply(s)
report['restroom_patches']=load_module(ART/'passenger_lodge_restrooms_01/scripts/opening_patch.py','plr_patch').apply()
# Rebuild planar UVs on patched shell faces, including newly created reveal faces.
shell_manifest=read(ART/'passenger_lodge_shell_01/shell_manifest.json')
for name in shell_manifest['material_changed_objects']:
 o=s.objects[name]
 if not name.startswith('FIT_'):continue
 uv=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  f.material_index=0
  normal=o.matrix_world.to_3x3()@f.normal;drop=max(range(3),key=lambda i:abs(normal[i]));a,b=[i for i in range(3) if i!=drop]
  for li in f.loop_indices:
   q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[a]/3.2,q[b]/3.2)
# Trim is subordinate to installed fittings. Remove only overlapping linear intervals,
# with a 2 mm end clearance, retaining the original trim cross-section/material.
assets=[o for p in report['packages'] for o in bpy.data.collections[p['collection']].all_objects if o.type=='MESH']
asset_bounds=[(o.name,bounds(o)) for o in assets]
trim=bpy.data.collections['PLSH_Shell_Trim']
for o in list(trim.objects):
 if not o.name.startswith(('PLSH_Skirting','PLSH_Dado','PLSH_Cornice')):continue
 lo,hi=bounds(o);axis=0 if hi[0]-lo[0]>hi[1]-lo[1] else 1
 cuts=[]
 for name,(al,ah) in asset_bounds:
  if all(min(hi[i],ah[i])-max(lo[i],al[i])>.0001 for i in range(3)):
   cuts.append((max(lo[axis],al[axis]-.002),min(hi[axis],ah[axis]+.002),name))
 if not cuts:continue
 runs=[(lo[axis],hi[axis])]
 for a,b,_ in sorted(cuts):
  runs=[r for x,y in runs for r in ([(x,min(a,y))] if x<a else [])+([(max(b,x),y)] if y>b else []) if r[1]-r[0]>.003]
 old=o.name;mats=list(o.data.materials)
 for index,(a,b) in enumerate(runs):
  l=lo.copy();h=hi.copy();l[axis]=a;h[axis]=b
  bpy.ops.mesh.primitive_cube_add(size=1,location=[(l[i]+h[i])/2 for i in range(3)])
  n=bpy.context.object;n.name=old+'_Integrated_'+str(index);n.dimensions=[h[i]-l[i] for i in range(3)]
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for owner in list(n.users_collection):owner.objects.unlink(n)
  trim.objects.link(n)
  for mat in mats:n.data.materials.append(mat)
 bpy.data.objects.remove(o,do_unlink=True)
 report['trim_repairs'].append({'original':old,'cuts':cuts,'retained_intervals':runs})
# Keep review equipment separate and remove stale scene copies from this deliverable.
review=bpy.data.collections.new('PLI_REVIEW_ONLY');s.collection.children.link(review)
for o in list(s.objects):
 if o.type in {'LIGHT','CAMERA'} and o.name.startswith('PLSH_'):
  for c in list(o.users_collection):c.objects.unlink(o)
  review.objects.link(o)
for other in list(bpy.data.scenes):
 if other!=s:bpy.data.scenes.remove(other)
roof=bpy.data.collections['PL03_Removable_Roof'];roof.hide_render=False;roof.hide_viewport=False
def layers(lc):
 if lc.collection==roof:lc.exclude=False;lc.hide_viewport=False
 for child in lc.children:layers(child)
layers(s.view_layers[0].layer_collection)
bpy.context.view_layer.update()
for o in list(roof.objects):
 if o is not None:o.hide_set(False);o.hide_render=False
s.frame_set(1);bpy.context.view_layer.update()
report['baseline']=baseline
report['patched_objects']=sorted(set(p['source_object'] for p in read(ART/'passenger_lodge_doors_01/wall_patches.json')['patches'])|set(p['object'] for p in report['restroom_patches']))
report['final_asset_state']={o.name:signature(o) for o in assets if o.name in s.objects}
report['source_unchanged']=sha(source)==expected and sha(shell)==report['shell_sha256']
assert report['source_unchanged']
# Resolve images before changing the current blend directory.
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  resolved=Path(bpy.path.abspath(im.filepath))
  if not resolved.exists():
   matches=list(ART.glob('passenger_lodge_*/**/'+Path(im.filepath).name))
   assert matches,'Missing image '+im.filepath
   im.filepath=str(matches[0])
  im.pack()
cut=s.view_layers.new('Cutaway')
def hide_roof(lc):
 if lc.collection==roof:lc.exclude=True
 for child in lc.children:hide_roof(child)
hide_roof(cut.layer_collection);cut.use=False
(OUT/'reconciliation.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Integrated.blend'),compress=True)
print('INTEGRATION SAVED',flush=True)
