import unreal,json
from pathlib import Path
r={}
for n in ['CubeBuilder','BrushBuilder','KillZVolume']:
 c=getattr(unreal,n,None)
 if c:r[n]={p:getattr(c,p).__doc__ for p in dir(c) if p in ['build','get_brush_builder','set_brush_builder']}
(Path(__file__).resolve().parents[1]/'revision06/volume_api.json').write_text(json.dumps(r))
