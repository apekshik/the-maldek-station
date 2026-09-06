import bpy
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
OUT=Path(__file__).resolve().parents[1]
C={c.name:c for c in scene.collection.children}
def col(n):
 if n not in C:C[n]=bpy.data.collections.new(n);scene.collection.children.link(C[n])
 return C[n]
def remove(o):bpy.data.objects.remove(o,do_unlink=True)
def meshob(n,v,f,c,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);col(c).objects.link(o)
 if m:me.materials.append(m)
 o['export_geometry']=False;o['collision']=False;return o
def cube(n,p,s,c,m):
 x,y,z=s;v=[(a*x/2,b*y/2,d*z/2) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=meshob(n,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],c,m);o.location=p;return o
def beam(n,a,b,w,c,m):
 a,b=Vector(a),Vector(b);o=cube(n,(a+b)/2,(w,w,(b-a).length),c,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mat(n,color,rough=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
steel=bpy.data.materials['R02_Chipped_Painted_Steel'];concrete=bpy.data.materials['R02_Weathered_Concrete'];soil=bpy.data.materials['R02_Cliff_Rock_and_Forest_Soil']

fog=bpy.data.materials['R02_Valley_Fog'];v=next(n for n in fog.node_tree.nodes if n.type=='PRINCIPLED_VOLUME')
# Keep thick mist down in the valley while reducing haze at the lamp/camera height.
n=fog.node_tree.nodes;l=fog.node_tree.links;geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=-7;r.inputs['From Max'].default_value=6;r.inputs['To Min'].default_value=.023;r.inputs['To Max'].default_value=.0015;l.new(sep.outputs['Z'],r.inputs['Value']);l.new(r.outputs['Result'],v.inputs['Density'])
# Glazed side windows catch rain-light reflections; the boarding aperture stays open.
glass=mat('R03_Wet_Gondola_Glass',(.38,.48,.52),.12);gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=.96;gp.inputs['IOR'].default_value=1.45
n=glass.node_tree.nodes;l=glass.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.28;b.inputs['Distance'].default_value=.002;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],gp.inputs['Normal'])
for loc,size in [((-1.55,8.05,5.475),(.012,4.26,1.15)),((1.55,8.05,5.475),(.012,4.26,1.15)),((0,11.05,5.475),(2.4,.012,1.15))]:
 o=cube('Gondola_Wet_Glass',loc,size,'12_Gondola',glass);world=o.matrix_world.copy();o.parent=bpy.data.objects['Gondola_MOVE_THIS'];o.matrix_world=world
for o in list(col('12_Gondola').objects):
 if o.type=='MESH' and 'Glass' not in o.name:
  mod=o.modifiers.new('Soft_Sheet_Edges','BEVEL');mod.width=.025;mod.segments=3

# Remove any study rain streaks sheltered by the station canopy.
o=bpy.data.objects['Rain_Streaks_Static_Render_Study'];vs=[];fs=[]
for poly in o.data.polygons:
 p=o.data.vertices[poly.vertices[0]].co
 if -8.2<p.x<8 and p.y<7.2 and p.z<7.6:continue
 a=len(vs);vs.extend([tuple(o.data.vertices[i].co) for i in poly.vertices]);fs.append(tuple(range(a,len(vs))))
me=bpy.data.meshes.new('Shelter_Masked_Rain');me.from_pydata(vs,[],fs);me.materials.append(o.data.materials[0]);o.data=me

cam=bpy.data.objects['CAM_R03_Platform_Rain'];cam.location=(-7,1,4.9);cam.rotation_euler=(Vector((0,10,5.3))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.exposure=-.35
scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_night_03.blend'))
for name,c in [('platform_rain',cam),('control_room_night',bpy.data.objects['CAM_R03_Control_Room']),('relay_terrain',bpy.data.objects['CAM_R03_Relay_Terrain']),('cable_route',bpy.data.objects['CAM_R03_Cable_Route'])]:
 scene.camera=c;scene.render.filepath=str(OUT/'previews'/f'{name}.png');print('REFINED_RENDER',name,flush=True);bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'millford_v2_night_03.blend'))

# A separate daylight layout proof makes the filled shoulder and smooth route reviewable.
# Do not save these temporary lighting settings over the night scene.
scene.camera=bpy.data.objects['CAM_R03_Relay_Terrain']
scene.view_settings.exposure=0
for n in scene.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=.4
bpy.data.objects['Overcast_Sun'].data.energy=1.5
for o in bpy.data.collections['17_Atmosphere'].objects:o.hide_render=True
scene.cycles.samples=24;scene.render.resolution_percentage=80
scene.render.filepath=str(OUT/'previews/relay_daylight_layout.png');print('RENDER daylight_layout',flush=True);bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
