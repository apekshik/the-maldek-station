import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]/'art/unreal_handoff/revision12/police_tape/wrap_fit';rows=json.loads((root/'survey.json').read_text())
for file in sorted(set(r['fbx'] for r in rows)):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=file,use_anim=False)
 print(file,flush=True)
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   points=[ob.matrix_world@v.co for v in ob.data.vertices]
   print(ob.name,len(points),[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)],flush=True)
