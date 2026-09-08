"""Remove superseded drive machinery by source name, preserving the room and collision."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();h=Handoff(source,deps,'gondola_mechanism/fbx');manifest=json.loads((OUT/'handoff_manifest.json').read_text());rows=[]
for row in manifest['chunks']:
 if row['name'] not in ['SM_R12_04_Lower_Drive_000_solid','SM_R12_04_Lower_Drive_005_solid']:continue
 keep=[n for n in row['sources'] if not n.startswith('R04_')]
 objects=[bpy.data.objects[n] for n in keep]
 new=h.chunk(row['name'].replace('SM_R12_','SM_GM_Shell_'),objects,pivot=row['pivot'],role=row['role'],surface=row['physical_surface'],exposure='Exterior')
 new['replace_label']=row['name'].replace('SM_R12_','R12_');new['removed']=[n for n in row['sources'] if n not in keep];rows.append(new)
(OUT/'gondola_mechanism/lower_shell.json').write_text(json.dumps(rows,indent=2));print('LOWER_SHELL_PRESERVED',[(r['name'],len(r['removed'])) for r in rows])
