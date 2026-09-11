import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend'
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Office.blend'))
s=bpy.context.scene;c=bpy.data.collections['WSP_ASSETS'];a=json.loads((P/'assembly.json').read_text());s.frame_set(1)
report={'scope':'Saved and reopened Blender evaluated assets. Conservative sampled box walking/trolley tests; not Unreal collision.','source_immutable':hashlib.sha256(SRC.read_bytes()).hexdigest()==a['source_sha256'],'topology_errors':[],'meshes':0,'objects':len(c.objects),'missing_uv':[],'inventory':{}}
def bounds(o,dg=None):
 o=o.evaluated_get(dg or bpy.context.evaluated_depsgraph_get());pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
for o in c.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces)
 if bad or deg:report['topology_errors'].append([o.name,bad,deg])
 if not me.uv_layers:report['missing_uv'].append(o.name)
 report['meshes']+=1;report['inventory'][o.name]={'bounds':bounds(o),'materials':[m.name for m in me.materials],'faces':len(me.polygons)};bm.free();ev.to_mesh_clear()
def overlap(b,lo,hi):return all(b[1][i]>lo[i]+1e-5 and b[0][i]<hi[i]-1e-5 for i in range(3))
def obstacles():return [(o.name,bounds(o)) for o in c.objects if o.type=='MESH']
def test_path(name,segments,hx,hy,height):
 obs=obstacles();hits=[];n=0
 for a0,b0 in zip(segments,segments[1:]):
  va=Vector(a0);vb=Vector(b0);steps=max(1,math.ceil((vb-va).length/.04))
  for i in range(steps+1):
   p=va.lerp(vb,i/steps);n+=1;lo=[p.x-hx,p.y-hy,.02];hi=[p.x+hx,p.y+hy,height]
   for on,bb in obs:
    if 'Trolley' in on or 'Caster' in on or 'Wheel' in on:continue
    if overlap(bb,lo,hi):hits.append(on)
 return {'name':name,'samples':n,'box_half_widths':[hx,hy],'height':height,'hits':sorted(set(hits)),'passed':not hits}
s.frame_set(40)
# Main entrance opened, cabinet/drawer close for ordinary transit.
for m in a['mechanisms']:
 if m['object'] not in ['WSP_Door_hinge']:
  o=bpy.data.objects[m['object']];getattr(o,'rotation_euler' if m['kind']=='ROTATION' else 'location')[m['axis']]=m['rest']
bpy.context.view_layer.update()
report['routes']=[test_path('Porch_entry_handling',[(6.9,1.94,0),(3.4,1.94,0),(3.4,3.2,0)],.34,.34,1.8),test_path('Rear_shelf_approach',[(3.4,2.3,0),(1.45,2.3,0),(1.45,4.1,0)],.34,.34,1.8),test_path('Counter_operator',[(3.5,2.8,0),(3.85,3.7,0)],.34,.34,1.8),test_path('Trolley_straight_entry',[(6.8,1.99,0),(3.35,1.99,0)],.6,.4,1.1)]
# Rotating .8x1.2 trolley at centre of reserved 2.2m handling zone: conservative enclosing AABB at 5deg samples.
obs=obstacles();hits=[]
for deg in range(0,91,5):
 an=math.radians(deg);hx=.6*math.cos(an)+.4*math.sin(an);hy=.6*math.sin(an)+.4*math.cos(an)
 for n,b in obs:
  if overlap(b,[3.15-hx,2.75-hy,.02],[3.15+hx,2.75+hy,1.1]):hits.append(n)
report['trolley_turn']={'centre':[3.15,2.75],'angles_degrees':list(range(0,91,5)),'hits':sorted(set(hits)),'passed':not hits}
seal=[bounds(o) for o in c.objects if o.name.startswith('WSP_Door_jamb_seal')];seal.sort(key=lambda b:b[0][1]);head=bounds(bpy.data.objects['WSP_Door_head_seal']);threshold=bounds(bpy.data.objects['WSP_Threshold']);width=seal[1][0][1]-seal[0][1][1];height=head[0][2]-threshold[1][2]
report['opening']={'rough':[1.5,2.35],'finished_clear':[width,height],'threshold_height':threshold[1][2],'passed':width>=1.30 and height>=2.15}
report['sweeps']={}
for m in a['mechanisms']:
 o=bpy.data.objects[m['object']];pts=[]
 for f in range(1,41):
  s.frame_set(f);bpy.context.view_layer.update()
  for ch in [o]+list(o.children_recursive):
   if ch.type=='MESH':pts.extend(bounds(ch))
 if pts:report['sweeps'][o.name]={'sampled_frames':40,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]}
s.frame_set(1)
report['anchors_passed']=all(bpy.data.objects.get(n) for n in a['anchors'])
report['asset_only']=all(o.type not in ['CAMERA','LIGHT'] for o in c.objects) and len(s.objects)==len(c.objects)
report['passed']=report['source_immutable'] and not report['topology_errors'] and not report['missing_uv'] and report['asset_only'] and all(r['passed'] for r in report['routes']) and report['trolley_turn']['passed']
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['inventory','sweeps']},indent=2))
