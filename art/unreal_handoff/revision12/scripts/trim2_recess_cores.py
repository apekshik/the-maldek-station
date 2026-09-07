"""Separate concealed wall faces from jamb/header skins in immutable-source export copies."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();manifest=json.loads((OUT/'handoff_manifest.json').read_text());h=Handoff(source,deps,'fbx')
cores=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Insulated_wall_core')]
window_repair=globals().get('WINDOW_REPAIR',False)
prefixes=('Door_return','Door_lintel','Window_return','Window_head_sill') if window_repair else ('Door_return','Door_lintel')
trims=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)]
edits=[];planes={}
for t in trims:
 lo,hi=bounds(t);axis=2 if t.name.startswith(('Door_lintel','Window_head_sill')) else min(range(2),key=lambda k:hi[k]-lo[k])
 for c in cores:
  a,z=bounds(c)
  if not all(min(hi[k],z[k])-max(lo[k],a[k])>.01 for k in range(3) if k!=axis):continue
  for side in [0,1]:
   face=[a,z][side][axis]
   if min(abs(face-lo[axis]),abs(face-hi[axis]))>.00001:continue
   planes.setdefault(c.name,set()).add((axis,side,round(face,5)))
   edits.append({'core':c.name,'trim':t.name,'axis':axis,'side':side,'plane':face,'recess_metres':.004})
assert planes
for name,faces in planes.items():
 c=bpy.data.objects[name];c.data=c.data.copy();inv=c.matrix_world.inverted()
 for v in c.data.vertices:
  p=c.matrix_world@v.co
  for axis,side,face in faces:
   if abs(p[axis]-face)<.00002:p[axis]+=.004 if side==0 else -.004
  v.co=inv@p
 c.data.update()
# Preserve the previously accepted quarters beam/floor separation if a changed assembly contains it.
for name in ['Cantilever_transfer_beam','Cantilever_transfer_beam.001']:
 c=bpy.data.objects.get(name)
 if c:
  c.data=c.data.copy();top=max(v.co.z for v in c.data.vertices)
  for v in c.data.vertices:
   if abs(v.co.z-top)<.00001:v.co.z-=.003
bpy.context.view_layer.update();h.deps=bpy.context.evaluated_depsgraph_get();changed=[]
export_cores={e['core'] for e in edits if e['trim'].startswith('Window_')} if window_repair else set(planes)
assert export_cores
for i,row in enumerate(list(manifest['chunks'])):
 if not set(row['sources'])&export_cores:continue
 objects=[bpy.data.objects[n] for n in row['sources']+row.get('source_collision_guides',[])]
 exposure=next(v.get('exposure') for v in manifest['materials'].values() if v['slot']==row['material_slots'][0])
 new=h.chunk(row['name'],objects,pivot=row['pivot'],role=row['role'],surface=row['physical_surface'],targets=row['replacement_targets'],exposure=exposure)
 assert new['material_slots']==row['material_slots']
 assert new['collision_boxes']==row['collision_boxes'],'Wall cores should have no independent blocking collision'
 manifest['chunks'][i]={**row,**new};changed.append(row['name'])
(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2));h.save('window_core_recess_export' if window_repair else 'door_core_recess_export')
(OUT/('window_fix' if window_repair else 'trim2')/'core_recess.json').write_text(json.dumps({'source_sha256':EXPECTED,'approved_source_modified':False,'edits':edits,'changed_assets':changed,'collision_unchanged':True,'export_cores':sorted(export_cores)},indent=2));print('RECESSED',len(export_cores),'CORES;',len(changed),'ASSEMBLIES',flush=True)
