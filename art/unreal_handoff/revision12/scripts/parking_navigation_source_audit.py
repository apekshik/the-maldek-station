import bpy,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(b/'parking/handoff.blend'),load_ui=False)
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.name in ['SM_VF10_Parking_Forest_Connector','SM_VF10_Parking_Furniture']:
  rows.append({'name':o.name,'vertices':[list(v.co) for v in o.data.vertices] if 'Connector' in o.name else [],'materials':[m.name for m in o.data.materials]})
(out/'source_audit.json').write_text(json.dumps(rows,indent=2))
