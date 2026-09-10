import bpy,json,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
# Limit reference evaluation to the lodge vicinity for these interior reviews.
for o in bpy.data.collections['PLR_REFERENCE_ONLY'].objects:
 if o.type=='MESH':
  bb=[o.matrix_world@Vector(p) for p in o.bound_box]
  if max(p.x for p in bb)<-17 or min(p.x for p in bb)>-9 or max(p.y for p in bb)<-14 or min(p.y for p in bb)>-5:o.hide_render=True
views=[('01_hallway_east',(8.8,12.35,1.65),(12.4,13.0,1.35),20,1),('02_hallway_west',(12.7,12.35,1.65),(9.1,12.5,1.35),20,1),('03_women_interior',(10.48,13.75,1.65),(9.15,15.55,.95),19,40),('04_men_interior',(11.55,13.8,1.65),(13.0,15.45,1.0),19,40),('05_basin_detail',(9.65,14.5,1.42),(8.46,14.18,.86),35,1),('06_stall_hardware',(9.27,14.28,1.40),(9.12,15.31,1.14),48,1),('07_women_entry_inside',(9.75,14.7,1.65),(10.45,13.1,1.2),24,1),('08_men_entry_inside',(12.0,14.7,1.65),(12.45,13.1,1.2),24,1),('10_men_basin_detail',(12.1,14.65,1.45),(13.54,14.50,.84),35,1),('11_urinal_detail',(12.65,16.30,1.45),(13.59,15.83,.95),32,1),('12_wc_detail',(8.9,15.65,1.50),(8.85,16.43,.48),26,40),('13_basin_interior',(9.3,14.2,1.95),(8.46,14.18,.74),40,1),('14_women_entry_front',(10.45,11.55,1.65),(10.45,13.15,1.25),18,1),('15_men_entry_front',(12.45,11.55,1.65),(12.45,13.15,1.25),18,1),('09_all_swings',(11,14.3,9.5),(11,14.3,0),35,40)]
def W(p):return Vector((p[0]-24.1,4-p[1],p[2]+4))
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
records=[]
for name,pos,target,lens,frame in views:
 if selected and name not in selected:continue
 s.frame_set(frame)
 for ob in bpy.data.collections['PLR_REVIEW_ONLY'].objects:
  if ob.type=='MESH':ob.hide_render=name!='09_all_swings'
 d=bpy.data.cameras.new('PLR_REVIEW_'+name);o=bpy.data.objects.new(d.name,d);bpy.data.collections['PLR_REVIEW_ONLY'].objects.link(o);o.location=W(pos);o.rotation_euler=(W(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.025;s.camera=o
 if name=='09_all_swings':d.type='ORTHO';d.ortho_scale=7.4
 s.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
 records.append(dict(name=name,camera_local=pos,target_local=target,frame=frame,temporary_review_lighting=True,roof_hidden=True))
(P/'previews'/('views_'+(selected[0] if selected else 'all')+'.json')).write_text(json.dumps(records,indent=2))

if not selected:
 s.frame_set(40)
 for ob in bpy.data.collections['PLR_REVIEW_ONLY'].objects:
  if ob.type=='MESH':ob.hide_render=True
 s.camera=bpy.data.objects['PLR_REVIEW_03_women_interior']
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'),compress=True)

if selected and (P/'previews/views_all.json').exists():
 existing=json.loads((P/'previews/views_all.json').read_text());byname={r['name']:r for r in existing};byname.update({r['name']:r for r in records})
 (P/'previews/views_all.json').write_text(json.dumps(list(byname.values()),indent=2))
