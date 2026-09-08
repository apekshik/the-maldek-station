"""Reopen the study, inspect evaluated geometry and sample the full animation."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Gondola_Cabin.blend'));s=bpy.context.scene;s.frame_set(60);deps=bpy.context.evaluated_depsgraph_get()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
report={'success':False,'scope':'Blender design validation; Unreal collision and state-machine integration remain pending','checks':{}}
def check(n,v):
 report['checks'][n]=bool(v)
 if not v:
  (out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise AssertionError(n)
removed=json.loads((out/'design_manifest.json').read_text())['removed_replaced_objects']
check('replaced_old_handles_track_sill_removed',not any(bpy.data.objects.get(n) for n in removed))
maximum=0;preserved=0
for old in json.loads((out/'audit.json').read_text()):
 o=bpy.data.objects.get(old['name'])
 if not o or old['name'] in removed or o.type!='MESH':continue
 b=bounds(o);wanted=[[old[k][i]-[0,8.05,4][i] for i in range(3)] for k in ['lo','hi']]
 maximum=max(maximum,max(abs(b[j][i]-wanted[j][i]) for i in range(3) for j in range(2)));preserved+=1
check('retained_shell_world_bounds_preserved',maximum<.001);report['preserved_meshes']=preserved;report['maximum_shell_bounds_error_m']=maximum
for name,sign in [('Gondola_South_Pier',-1),('Gondola_South_End',1)]:
 o=bpy.data.objects[name];inv=o.matrix_world.inverted();hit=o.ray_cast(inv@Vector((sign*1.1,-3.6,1.49)),inv.to_3x3()@Vector((0,1,0)))
 check(name+'_glazing_core_is_open',not hit[0])
bad=[];tris=0;count=0
for o in s.objects:
 if not o.name.startswith('GC_') or o.type not in {'MESH','CURVE'}:continue
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);bm=bmesh.new();bm.from_mesh(me)
 if any(not e.is_manifold for e in bm.edges):bad.append(o.name)
 tris+=sum(len(f.verts)-2 for f in bm.faces);count+=1;bm.free();bpy.data.meshes.remove(me)
report.update(new_evaluated_objects=count,new_triangles=tris,non_manifold_objects=bad);check('new_solid_meshes_manifold',not bad)
left=bpy.data.objects['GC_SLIDE_LEFT'];right=bpy.data.objects['GC_SLIDE_RIGHT'];cab=bpy.data.objects['GC_CABIN_APPROACH_ROOT'];pinion=bpy.data.objects['GC_DRIVE_PINION'];samples=[]
for f in range(1,385):
 s.frame_set(f);q=right.location.x/.635
 check('leaf_pair_stays_symmetric',abs(left.location.x+right.location.x)<1e-5)
 check('slide_stays_in_travel_limits',-.0001<=q<=1.0001)
 check('closed_during_travel',abs(cab.location.y)<1e-5 or q<.0001)
 check('drive_matches_racks',abs(pinion.rotation_euler.y-q*.635/.034)<.002)
 if f in [1,60,78,120,162,264,306,348,384]:samples.append({'frame':f,'door_open_fraction':q,'cabin_y':cab.location.y})
s.frame_set(180);bpy.context.view_layer.update()
check('both_leaves_fully_open',abs(left.location.x+.635)<1e-5 and abs(right.location.x-.635)<1e-5)
leaf_geometry=[o for c in [bpy.data.collections['02_Left_sliding_leaf'],bpy.data.collections['03_Right_sliding_leaf']] for o in c.objects if o.name.startswith(('GC_Leaf_','GC_Soft_','GC_Replaceable_'))]
check('open_leaves_clear_structural_width',all(bounds(o)[1][0]<=-.600 or bounds(o)[0][0]>=.600 for o in leaf_geometry))
check('rack_stays_within_guarded_span',all(abs(o.location.x)+.635+.65<=1.35 for o in s.objects if o.name.startswith('GC_Rack') and not o.name.startswith('GC_Rack_tooth')))
check('two_recorded_audio_cues',len(s.sequence_editor.strips)==2)
check('audio_packed',all(st.sound.packed_file for st in s.sequence_editor.strips))
check('rendered_shell_visible',not bpy.data.collections['12_Gondola'].hide_render and not bpy.data.objects['R04_Crowned_Roof'].hide_render)
report['sampled_frames']=384;report['key_frames']=samples;report['success']=True
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
