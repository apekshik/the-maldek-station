import bpy
from pathlib import Path
p=Path('art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend').resolve()
with bpy.data.libraries.load(str(p),link=False) as (a,b):
 print('CABIN_COLLECTIONS', [n for n in a.collections if any(k in n.lower() for k in ['gondola','12_'])])
 print('CABIN_OBJECTS', [n for n in a.objects if any(k in n.lower() for k in ['hanger','grip','gondola'])][:80])
