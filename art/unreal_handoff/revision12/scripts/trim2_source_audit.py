import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();rows=[]
for o in bpy.data.objects:
 if not o.type=='MESH' or not o.name.startswith(('Door_return','Door_lintel','Insulated_wall_core')):continue
 rows.append({'name':o.name,'bounds':bounds(o),'collections':[c.name for c in o.users_collection]})
(OUT/'trim2/source_openings.json').write_text(json.dumps(rows,indent=2))
