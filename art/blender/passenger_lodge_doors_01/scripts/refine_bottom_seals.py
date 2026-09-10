"""Ensure the lowered gasket bridges floor to leaf rather than leaving a light gap."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(__file__).resolve().parents[1]
def apply():
 s=bpy.context.scene;s.frame_set(1)
 for key,W,side in [('ARRIVAL',1.2,1),('GONDOLA',1.2,1),('STAFF',1.,-1)]:
  prefix='PLD_'+key+'_';seal=bpy.data.objects[prefix+'BOTTOM_SEAL'];slab=bpy.data.objects[prefix+'Leaf_Steel']
  if seal.get('continuous_bottom_seal'):continue
  for v in seal.data.vertices:v.co.z=.022+(v.co.z-.014)*3
  seal['continuous_bottom_seal']=True;seal['closed_z_bounds_m']='0 to .024';seal['retracted_z_bounds_m']='.010 to .034'
  bpy.context.view_layer.update()
  bpy.ops.mesh.primitive_cube_add(size=1);tool=bpy.context.object
  tool.matrix_world=slab.matrix_world@Matrix.Translation(Vector((W/2,side*.0525,.0315)))@Matrix.Diagonal(Vector((W+.020,.014,.029,1)))
  mod=slab.modifiers.new('Bottom_gasket_cartridge_slot','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
  bpy.context.view_layer.objects.active=slab;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
 bpy.context.view_layer.update()
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'));bpy.context.window.scene=bpy.data.scenes['PLD_Fitted_Doors'];apply()
 data=json.loads((OUT/'replacement_manifest.json').read_text())
 for rec in data['objects']:
  ob=bpy.data.objects[rec['name']];rec['dimensions']=list(ob.dimensions)
 (OUT/'replacement_manifest.json').write_text(json.dumps(data,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Doors.blend'),compress=True)
