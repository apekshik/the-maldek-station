"""Read-only external-image and linked-library inventory for checkpoint sources."""
import bpy,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3]
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=root,text=True).splitlines()
report=[]
for rel in paths:
 if not rel.endswith('.blend'):continue
 path=root/rel
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
 images=[]
 for im in bpy.data.images:
  if im.source not in {'FILE','TILED','SEQUENCE','MOVIE'}:continue
  external=Path(bpy.path.abspath(im.filepath,library=im.library))
  images.append({'name':im.name,'path':str(external),'packed':bool(im.packed_file or im.packed_files),'exists':external.exists()})
 libraries=[{'path':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).exists()} for l in bpy.data.libraries]
 report.append({'file':rel,'images':images,'libraries':libraries})
 (root/'art/checkpoints/pre_vf07/blender_dependencies.json').write_text(json.dumps(report,indent=2))
print('CHECKPOINT_DEPENDENCY_AUDIT_COMPLETE',len(report),flush=True)
