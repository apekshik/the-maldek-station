import bpy, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
stage=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'before'
(OUT/'audit'/stage).mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='OPTIX';p.refresh_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.view_settings.exposure=0
for l in s.view_layers:l.use=l.name=='02_Full_Shell'
bpy.context.window.view_layer=s.view_layers['02_Full_Shell']
targets=['12_Gondola','02_Control_Room','04_Lower_Drive','01_Upper_Platform']
inventory={}
for c in targets:
 inventory[c]=[]
 for o in bpy.data.collections[c].objects:
  if o.type!='MESH':continue
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  inventory[c].append(dict(name=o.name,lo=[min(v[i] for v in bb) for i in range(3)],hi=[max(v[i] for v in bb) for i in range(3)],loc=list(o.location),dimensions=list(o.dimensions),parent=o.parent.name if o.parent else None,hidden=o.hide_render,materials=[m.name for m in o.data.materials],modifiers=[dict(name=m.name,type=m.type,width=m.width if m.type=='BEVEL' else None) for m in o.modifiers]))
(OUT/'audit'/f'{stage}_inventory.json').write_text(json.dumps(inventory,indent=2))
original={o.name:o.hide_render for o in s.objects}
for o in s.objects:o.hide_render=True
world=bpy.data.worlds.new('Audit_Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.34,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
def light(n,pos,target,power,size):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size
 o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
camd=bpy.data.cameras.new('Audit');cam=bpy.data.objects.new('Audit',camd);s.collection.objects.link(cam);s.camera=cam
views=[('gondola','12_Gondola',(-8,1.0,7.8),(0,8,5.2),42),('control_room','02_Control_Room',(-3.6,-3.4,5.8),(-6.2,-.65,5.15),27),('lower_drive','04_Lower_Drive',(5.8,10.8,3.4),(1.6,6.2,1),42),('platform','01_Upper_Platform',(-9,1,7.5),(-2,5.5,4),37)]
for name,col,pos,target,lens in views:
 for o in s.objects:
  if o.type not in ('CAMERA',):o.hide_render=True
 for o in bpy.data.collections[col].objects:o.hide_render=original.get(o.name,False)
 if name=='gondola':
  for o in bpy.data.objects:
   if o.name.startswith('Gondola_Roof') and not o.get('collision_only'):o.hide_render=False
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=lens
 key=light('Audit_Key',Vector(target)+Vector((-4,-4,7)),target,1800,6)
 fill=light('Audit_Fill',Vector(target)+Vector((4,3,5)),target,1200,5)
 s.render.filepath=str(OUT/'audit'/stage/f'{name}.png');bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
 bpy.data.objects.remove(key,do_unlink=True);bpy.data.objects.remove(fill,do_unlink=True)
print('AUDIT_COMPLETE',stage,flush=True)
