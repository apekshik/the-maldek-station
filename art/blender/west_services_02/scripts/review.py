import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];ART=OUT.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Station_West_Integrated.blend'));s=bpy.data.scenes['Station_West_Services_Integrated'];bpy.context.window.scene=s
(OUT/'previews').mkdir(exist_ok=True)
a=json.loads((ART/'west_services_power_01/assembly.json').read_text())
def pose(frame):
 s.frame_set(frame)
 for m in a['mechanisms']:
  if m['pivot'].startswith('WSE_Door_hinge'):bpy.data.objects[m['pivot']].rotation_euler['XYZ'.index(m['axis'])]=math.radians(m['open_degrees'] if frame!=1 else 0)
 bpy.context.view_layer.update()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args or 'overview' in args:
 for name in ['01_Station','02_Wrap_platform','03_Upper_cutaway','04_Lower_wrap_plan','05_Arrival']:
  pose(40 if 'cutaway' in name else 1);s.camera=bpy.data.objects['WS02_'+name]
  original={o.name:o.hide_render for o in s.objects}
  if name=='03_Upper_cutaway':bpy.data.collections['WS_SHARED_ROOF'].hide_render=True
  if name=='04_Lower_wrap_plan':
   for ob in s.objects:
    if ob.type not in ['MESH','FONT','CURVE']:continue
    ps=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    if min(v.z for v in ps)>3.6:ob.hide_render=True
   for c in ['WS_SHARED_ROOF','WSP_ASSETS','WSR_ASSETS']:bpy.data.collections[c].hide_render=True
  s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
  for ob in s.objects:ob.hide_render=original[ob.name]
  for c in ['WS_SHARED_ROOF','WSP_ASSETS','WSR_ASSETS']:bpy.data.collections[c].hide_render=False
if not args or 'details' in args or 'roof' in args:
 # Keep all combined western context; omit distant lodge geometry for efficient close reviews.
 for ob in s.objects:
  if ob.type=='LIGHT':ob.hide_render=True
  if ob.type in ['MESH','CURVE','FONT'] and not ob.name.startswith(('WS_','WS02_','WSP_','WSR_','WSE_')):ob.hide_render=True
 s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000
 try:
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
  for d in prefs.devices:d.use=d.type=='OPTIX'
  if any(d.use for d in prefs.devices):s.cycles.device='GPU'
 except Exception:pass
 s.world=bpy.data.worlds.new('WS02_ReviewWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.52,.60,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6;s.view_settings.view_transform='AgX'
 c=bpy.data.collections['WS02_REVIEW_ONLY']
 for name,pos,target,power,size in [('Parcel',(-34.2,-2.5,7.15),(-34,-2.5,4.6),420,3),('Rescue',(-34.2,2.5,7.15),(-34,2.5,4.6),420,3),('Power',(-34.5,1,4.12),(-34,-1,1.2),550,3),('Porch',(-27,0,9),(-32,0,5),1500,8),('West',(-44,3,8),(-36,1,4),2200,9),('South',(-34,-12,10),(-34,0,4),1800,7)]:
  d=bpy.data.lights.new('WS02_TEMP_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;ob=bpy.data.objects.new(d.name,d);c.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('WS02_TEMP_Detail');cam=bpy.data.objects.new(d.name,d);c.objects.link(cam);s.camera=cam
 shots=[('06_Parcels',(-32.9,-2.25,6.25),(-36.3,-2.3,5.7),23,40),('07_Rescue',(-32.15,3.0,6.25),(-35.8,2.25,5.6),23,1),('08_Power',(-36.3,3.7,2.85),(-34.5,-1.8,2.2),23,40),('09_Porch',(-28.3,-6.6,6.3),(-32.2,.5,5.9),24,1),('10_Lower_door',(-40,4.4,2.9),(-36.2,2.2,2.3),24,1),('11_Spare_side',(-39,-7.0,2.85),(-33,-5.7,2),24,1)]
 shots.append(('12_Roof_interface',(-36.1,-6.6,8.95),(-35.2,-5.3,8.22),52,1))
 for name,pos,target,lens,f in shots:
  if 'roof' in args and name!='12_Roof_interface':continue
  pose(f);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)

