import unreal,json
from pathlib import Path
r={}
for c in ['Actor','InstancedFoliageActor','HierarchicalInstancedStaticMeshComponent']:
 cls=getattr(unreal,c);r[c]={n:getattr(cls,n).__doc__ for n in ['add_component_by_class','add_instances','add_instance','set_cull_distances'] if hasattr(cls,n)}
r['factories']=[n for n in dir(unreal) if 'Foliage' in n and 'Factory' in n]
(Path(__file__).resolve().parents[1]/'revision06/foliage_api.json').write_text(json.dumps(r,indent=2))
