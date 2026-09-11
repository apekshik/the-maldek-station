"""Replay on a future WORLD-coordinate integration COPY, never the frozen master."""
import bpy,math
from pathlib import Path
FROZEN=Path(__file__).resolve().parents[2]/'west_services_01/Maldek_West_Services_Blockout.blend'
def apply_world_patch():
 assert Path(bpy.data.filepath).resolve()!=FROZEN.resolve(), 'Immutable master: use an integration copy'
 ob=bpy.data.objects['WS_BaseSouth']
 assert not ob.get('WSE_sleeve_patch'), 'Already patched'
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.157,depth=.5,location=(-35.2,-4.875,3.15));cut=bpy.context.object;cut.rotation_euler[0]=math.pi/2
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('WSE south sleeve aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);ob['WSE_sleeve_patch']=True
if __name__=='__main__':apply_world_patch()
