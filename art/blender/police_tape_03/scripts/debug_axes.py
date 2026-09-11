from io_scene_fbx import parse_fbx
from pathlib import Path
for f in [Path(r'C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/police_tape/wrap_fit/SK_European_Beech_01_B.fbx'),Path(r'C:/Users/apek-anna/Developer/the-maldek-station/art/unreal_handoff/revision12/police_tape/wrap_fit/SM_PoliceTape_Wrap_0_0.fbx')]:
 data,ver=parse_fbx.parse(str(f));print(f.name)
 for a in data.elems:
  if a.id==b'GlobalSettings':
   for b in a.elems:
    for c in b.elems:print(c.props)
