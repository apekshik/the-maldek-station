import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Digital_Door_Variants.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
reader=bpy.data.collections['04_Digital_keypad'];keys=[o for o in reader.objects if o.name.startswith('Tactile_key_')];pivot=bpy.data.objects['D01_HINGE_PIVOT']
checks={'twelve_separate_buttons':len(keys)==12,'reader_attached_to_leaf':all(o.parent==pivot for o in reader.objects),'glass_preserved':bpy.data.objects['Vision_glass'].data.materials[0].name=='D01_Frosted_glass','no_mechanical_padlock':not any('Padlock_' in o.name or 'Hasp_' in o.name for o in s.objects)}
def bounds(o):
 v=[o.matrix_world@Vector(p) for p in o.bound_box];return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
checks['reader_below_glass']=max(bounds(o)[1][2] for o in reader.objects if o.type=='MESH')<bounds(bpy.data.objects['Vision_glass'])[0][2]
checks['buttons_clear_of_lever']=max(bounds(o)[1][0] for o in keys)<1.025
before={o.name:bounds(o) for o in bpy.data.collections['06_Electronic_strike'].objects};s.frame_set(90);bpy.context.view_layer.update()
checks['strike_remains_fixed']=before=={o.name:bounds(o) for o in bpy.data.collections['06_Electronic_strike'].objects}
report={'checks':checks,'success':all(checks.values()),'scope':'Blender design geometry; engine verification recorded separately.'};(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['success']
