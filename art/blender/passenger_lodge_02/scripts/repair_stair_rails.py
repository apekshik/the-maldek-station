import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
s=bpy.data.scenes['04_Combined_Station_Blockout'];bpy.context.window.scene=s
c=bpy.data.collections['PL02_New_Deck_Rails_and_Stair'];ret=bpy.data.collections['PL02_Retained_East_Rails_and_Supports'];steel=bpy.data.materials['Layout_Petrol_Enamel']
for node in ast.parse((OUT/'scripts/build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['bounds','beam','rail']:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
old_report=OUT/'stair_rail_repair.json'
removed=json.loads(old_report.read_text())['removed_old_guard_objects'] if old_report.exists() else []
for o in list(ret.objects):
 if o.type!='MESH' or not any(cc.name=='VF07_Public_Guards' for cc in o.users_collection):continue
 lo,hi=bounds(o)
 if ((lo[0]<-6.3 and hi[0]>-8.2 and lo[1]<-7.7 and hi[1]>-15.3) or (lo[0]<1.6 and hi[0]>-6.3 and lo[1]>-13.3 and hi[1]<-13.1)) and lo[2]>=3.99:
  ret.objects.unlink(o);removed.append(o.name)
for o in list(ret.objects):
 if o.type!='MESH' or not any(cc.name=='VF07_Deck_Structure' for cc in o.users_collection):continue
 lo,hi=bounds(o)
 if lo[0]<-6.35 and hi[0]>-8.05 and lo[1]<-7.75 and hi[1]>-15.1:
  ret.objects.unlink(o);removed.append(o.name)
for o in list(c.objects):
 if o.name.startswith(('PL02_Perimeter_4','PL02_Perimeter_5','PL02_Stair_','PL02_Landing_outer','PL02_Well_Guard','PL02_Safe_')):bpy.data.objects.remove(o,do_unlink=True)
# Continuous deck guards stand outside the stair opening, with access at the head.
rail('PL02_Safe_Left_Deck',(-8.2,-15.15),(-8.2,-7.7))
rail('PL02_Safe_Right_Deck',(-6.2,-13.2),(-6.2,-7.7))
# Keep the level upper landing open to the right; no guard across this route.
rail('PL02_Safe_East_Return',(-6.2,-13.2),(1.5,-13.2))
# Dedicated handrails follow the pitch; horizontal deck guards serve a different edge.
for side,x in [('Left',-8.1),('Right',-6.3)]:
 points=[(x,-16.22,0),(x,-14.7,0),(x,-14.42,4/24),(x,-7.84,4),(x,-7.7,4)]
 for h in [.55,1.1]:
  for a,b in zip(points,points[1:]):beam('PL02_Safe_'+side+'_Handrail',tuple(v+(h if i==2 else 0) for i,v in enumerate(a)),tuple(v+(h if i==2 else 0) for i,v in enumerate(b)),.03)
 for y,z in [(-16.22,0),(-14.7,0)]+[(-14.42+i*.28,(i+1)*4/24) for i in [0,4,8,12,16,20,23]]+[(-7.7,4)]:beam('PL02_Safe_'+side+'_Post',(x,y,z),(x,y,z+1.1),.035)
bpy.context.view_layer.update()
# No retained old guard is permitted to cross the flight interior.
for o in ret.objects:
 if o.type!='MESH' or not any(cc.name=='VF07_Public_Guards' for cc in o.users_collection):continue
 lo,hi=bounds(o)
 assert not(lo[0]<-6.35 and hi[0]>-8.05 and lo[1]<-7.75 and hi[1]>-15.1 and lo[2]>=3.99),o.name
(OUT/'stair_rail_repair.json').write_text(json.dumps({'removed_old_guard_objects':removed,'left_deck_guard_y':[-15.15,-7.7],'deck_guard_height_m':1.1,'handrails_both_sides':True,'old_guard_crossing_check_passed':True},indent=2))
def cam(name,pos,target,scale):
 o=bpy.data.objects.get(name)
 if not o:d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
 o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;return o
views=[cam('Stair_Close_Left',(-16,-21,13),(-8,-10.5,3.5),15),cam('Stair_Close_Right',(1,-21,10),(-7.2,-10.7,2.5),13),cam('Stair_Upper_Landing',(-12,-12,10),(-7.5,-7.5,4),8)]
eye=cam('Stair_Right_Access',(-3.5,-6.6,5.65),(-9,-7.2,4.8),8);eye.data.type='PERSP';eye.data.lens=24;views.append(eye)
s.camera=bpy.data.objects['PL02_Combined_Overview'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
for o in views+[bpy.data.objects['PL02_Combined_Overview'],bpy.data.objects['PL02_Combined_Plan']]:
 s.camera=o;s.render.filepath=str(OUT/'previews'/f'{o.name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=views[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
