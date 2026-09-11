import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'Millford_Service_Cassette.blend'))
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
checks={}
for x in [-21.25,21.25]:
 hit=scene.ray_cast(dg,Vector((x*.001,-.1,.0355)),Vector((0,1,0)),distance=.2)
 checks[f'reel_{x}_through_hole']=not hit[0]
checks['two_label_sides']=all(any(o.type=='FONT' and o.data.body==t for o in scene.objects) for t in ['NIGHT SHIFT - 14.11.86','RETURN TO CONTROL ROOM'])
checks['tape_ribbon']=bpy.data.objects.get('Exposed magnetic tape path') is not None
checks['packed_fonts']=all(f.packed_file is not None for f in bpy.data.fonts if f.filepath and f.filepath!='<builtin>')
checks['four_previews']=all((p/'previews'/f'{n}.png').exists() for n in ['01_hero','02_front','03_back','04_tape_edge'])
report={'checks':checks,'success':all(checks.values())};(p/'verification.json').write_text(json.dumps(report,indent=2));print(report)
assert report['success']
