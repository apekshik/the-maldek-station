import bpy,json
from pathlib import Path
p=Path('C:/Users/apek-anna/Developer/the-maldek-station')
bpy.ops.wm.open_mainfile(filepath=str(p/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'))
r=[]
for o in bpy.data.objects:
 if any(k in o.name for k in ['Motor','Reducer','Wheel','Brake','Bearing','Output_','Drive_']):r.append({'name':o.name,'position':list(o.location),'collections':[c.name for c in o.users_collection]})
(p/'art/unreal_handoff/revision12/gondola_mechanism/blender_audit.json').write_text(json.dumps(r,indent=2))
