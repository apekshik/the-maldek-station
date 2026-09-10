"""Append the existing station intact; stage a linked lodge beside it for reference."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
source=REPO/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
target=OUT/'Maldek_Passenger_Lodge_Layout.blend'
bpy.ops.wm.open_mainfile(filepath=str(target))
assert '03_Existing_Station_Reference' not in bpy.data.scenes,'Already appended; rebuild lodge first'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
 source_scenes=list(src.scenes);dst.scenes=source_scenes
station=dst.scenes[0];station.name='03_Existing_Station_Reference'
bpy.context.window.scene=station;bpy.context.view_layer.update()
# Appending preserves source transforms; record every imported mesh before any additions.
baseline={o.name:list(sum((list(row) for row in o.matrix_world),[])) for o in station.objects if o.type=='MESH'}
bundle=bpy.data.collections.new('PL01_Linked_Lodge_Assembly')
for n in ['PL01_Shell','PL01_Furniture_Footprints','PL01_Restroom_Fixtures','PL01_Labels_and_Clearances','PL01_Roof_Envelope']:
 bundle.children.link(bpy.data.collections[n])
instance=bpy.data.objects.new('NEW_LODGE_STAGING_ONLY_NOT_SITE_PLACEMENT',None)
instance.instance_type='COLLECTION';instance.instance_collection=bundle;instance.location=(-43,0,4);station.collection.objects.link(instance)
instance['placement_status']='Staged outside existing west deck for comparison; not an approved site transform or a connected platform.'
instance['edit_geometry_in_scene']='01_Lodge_Layout'
cu=bpy.data.curves.new('Reference_note','FONT');cu.body='EXISTING STATION: RETAINED GEOMETRY\nNEW LODGE: STAGED FOR COMPARISON / NOT PLACED';cu.size=.65
note=bpy.data.objects.new('STAGING_EXPLANATION',cu);station.collection.objects.link(note);note.location=(-44,-23,4.1);cu.materials.append(bpy.data.materials['Layout_Brass_Markers'])
cam_data=bpy.data.cameras.new('Station_and_Lodge_Review');cam=bpy.data.objects.new('Station_and_Lodge_Review',cam_data);station.collection.objects.link(cam)
cam.location=(-53,-49,43);cam.rotation_euler=(Vector((-17,-2,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=70;station.camera=cam
station.render.engine='CYCLES';station.cycles.samples=16;station.cycles.use_denoising=True;station.render.resolution_x=1600;station.render.resolution_y=1100;station.render.resolution_percentage=100
# Existing presentation lights stay; add only a clearly named review fill.
ld=bpy.data.lights.new('PL01_Context_Review_Fill','AREA');ld.energy=12000;ld.shape='DISK';ld.size=35
lo=bpy.data.objects.new('PL01_Context_Review_Fill',ld);station.collection.objects.link(lo);lo.location=(-22,-5,30)
bpy.context.window.scene=station
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
changed=[n for n,m in baseline.items() if list(sum((list(row) for row in bpy.data.objects[n].matrix_world),[]))!=m]
assert not changed,changed[:10]
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'source':str(source),'source_sha256':source_hash,'imported_meshes':len(baseline),'changed_source_transforms':changed,'source_file_unchanged':True,'reference_scene':station.name,'lodge_staging_offset_m':list(instance.location),'site_placement_approved':False,'contains':'Actual appended source platform, grating, railings, stairs, control, quarters, terrain and station assemblies; not bounding-box substitutes.'}
(OUT/'station_reference.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(target))
station.render.filepath=str(OUT/'previews/06_Station_Reference.png');bpy.ops.render.render(write_still=True,scene=station.name)
bpy.ops.wm.save_as_mainfile(filepath=str(target))
