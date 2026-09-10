import bpy,json,sys,math,hashlib,struct
from mathutils import Matrix,Vector
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'))
s=bpy.data.scenes['PLD_Fitted_Doors'];bpy.context.window.scene=s
views=json.loads((OUT/'review_views.json').read_text())
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args:views=[v for v in views if any(a in v['name'] for a in args)]
annotations=bpy.data.collections.new('PLD_REVIEW_ONLY_Plan_Annotations');s.collection.children.link(annotations)
def ink(n,color):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=.3
 return m
gold=ink('PLD_REVIEW_Swing_Amber',(.65,.26,.015));green=ink('PLD_REVIEW_Route_Green',(.015,.27,.08))
def line(n,pts,m,r=.009):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,q in zip(sp.points,pts):p.co=(*q,1)
 ob=bpy.data.objects.new(n,cu);annotations.objects.link(ob);cu.materials.append(m)
for d in json.loads((OUT/'replacement_manifest.json').read_text())['doors']:
 T=Matrix(d['matrix_world']);pivot=Vector(d['hinge_pivot_local']);tip=Vector((d['width']+.015,d['side']*.0525,.035));pts=[]
 for angle in range(0,101,2):
  q=T@(pivot+Matrix.Rotation(math.radians(d['side']*angle),3,'Z')@(tip-pivot));pts.append(q)
 line('PLD_REVIEW_'+d['id']+'_sweep',pts,gold)
# Door passage centreline and its .34 m body envelope, plus independent routes.
for name,a,b in [('Arrival',(-17.1,-12),(-17.1,-5.1)),('Gondola',(-17.1,1.6),(-17.1,5.5)),('Staff',(-21.5,-10.5),(-17.6,-10.5)),('Queue',(-17.1,-5.7),(-21.1,-5.7)),('Grating',(-22,5.5),(-12,5.5))]:
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);normal=(-dy/length,dx/length)
 for off in [-.34,0,.34]:line('PLD_REVIEW_Route_'+name,[(a[0]+off*normal[0],a[1]+off*normal[1],4.030),(b[0]+off*normal[0],b[1]+off*normal[1],4.030)],green,.006 if off else .010)
# CPU fallback is deterministic; use available CUDA/OptiX only if enabled by Blender.
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
for v in views:
 annotations.hide_render='_Plan_' not in v['name']
 s.frame_set(v['frame']);s.camera=bpy.data.objects[v['camera']]
 s.render.filepath=str(OUT/'previews'/(v['name']+'.png'))
 bpy.ops.render.render(write_still=True)
 print('RENDERED',v['name'],flush=True)
if not args:
 records=[]
 for v in views:
  p=OUT/'previews'/(v['name']+'.png');raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
  width,height=struct.unpack('>II',raw[16:24]);assert (width,height)==(1200,1000)
  records.append(dict(v,path='previews/'+p.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),dimensions=[width,height]))
 (OUT/'preview_manifest.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Doors.blend').read_bytes()).hexdigest(),render_count=len(records),renders=records),indent=2))
