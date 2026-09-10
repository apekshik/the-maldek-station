import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
s=bpy.data.scenes['04_Combined_Station_Blockout'];bpy.context.window.scene=s
c=bpy.data.collections['PL02_New_Deck_Rails_and_Stair'];steel=bpy.data.materials['Layout_Petrol_Enamel']
tree=ast.parse((OUT/'scripts/build.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['bounds','box','beam','rail']:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
# Rebuild west/north guards so intermediate posts follow the shorter edge too.
for ob in list(c.objects):
 if ob.name.startswith(('PL02_Perimeter_0','PL02_Perimeter_1')):bpy.data.objects.remove(ob,do_unlink=True)
rail('PL02_Perimeter_0',(-29.45,-15.15),(-29.45,7.35))
rail('PL02_Perimeter_1',(-29.45,7.35),(-4,7.35))
# Updated outer support ground contacts after narrowing.
probes=[]
bpy.context.view_layer.update()
terrain=bpy.data.objects['R11_Current_Terrain']
for ob in c.objects:
 if not ob.name.startswith('PL02_Support'):continue
 x,y=ob.location.x,ob.location.y
 origin=terrain.matrix_world.inverted()@Vector((x,y,3.6))
 hit,loc,_,_=terrain.ray_cast(origin,Vector((0,0,-1)),distance=40)
 if hit:
  z=(terrain.matrix_world@loc).z;ob.dimensions.z=3.8-z;ob.location.z=(3.8+z)/2
  probes.append({'xy':[x,y],'ground_z':z,'hit':terrain.name})
r=json.loads((OUT/'fit_report.json').read_text());r['support_probes']=probes
r['fixed_arrival']='Arrival assembly and turn moved 1.5 m west; source reference unchanged; ground approach requires fit validation.'
r['edge_refinement']={'west_promenade_m':5.35,'arrival_shift_x_m':-1.5,'stairwell_cut_through_deck':True,'obsolete_deck_tab_removed':True}
r.pop('validation',None)
(OUT/'fit_report.json').write_text(json.dumps(r,indent=2))
s.camera=bpy.data.objects['PL02_Combined_Overview'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
for name in ['PL02_Combined_Overview','PL02_Combined_Plan']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['PL02_Combined_Overview'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
