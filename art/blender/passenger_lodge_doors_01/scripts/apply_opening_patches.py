"""Replay only the recorded door-local cuts into a fresh package-owned source copy.

Run after build.py. Never saves the approved source. For integration into another
review copy, call apply(scene) explicitly; it modifies only listed source objects.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(__file__).resolve().parents[1]
def apply(scene):
 data=json.loads((OUT/'wall_patches.json').read_text())
 for p in data['patches']:
  o=scene.objects.get(p['source_object'])
  if o is None:raise RuntimeError('Expected original source object: '+p['source_object'])
  o.data=o.data.copy()
  bpy.ops.mesh.primitive_cube_add(size=1)
  tool=bpy.context.object;tool.name='PLD_TEMP_PATCH_CUTTER'
  tool.matrix_world=Matrix(p['matrix_world'])@Matrix.Translation(Vector(p['local_box_center']))@Matrix.Diagonal(Vector((*p['local_box_dimensions'],1)))
  mod=o.modifiers.new('PLD_'+p['door']+'_opening_cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(tool,do_unlink=True)
 return len(data['patches'])
if __name__=='__main__':
 data=json.loads((OUT/'wall_patches.json').read_text());source=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
 assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=scene
 count=apply(scene)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Opening_Patch_Review.blend'),compress=True)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
 print('Applied local cuts:',count)
