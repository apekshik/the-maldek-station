"""Separate terrain asset; preserves the current forest mesh outside the cliff."""
import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import height
b=Path(__file__).resolve().parents[1];out=b/'gorge'
data=json.loads((b/'forest_refine/terrain_grid.json').read_text())
vs=[(x,y,height(z,x,y)) for x,y,z in data['vertices']]
lookup={(round(x,3),round(y,3)):z for x,y,z in vs}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(b/'forest_refine/SM_Forest_Refined_Terrain.fbx'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)==1
o=objects[0];o.name='SM_Station_Gorge_Terrain'
for v in o.data.vertices:
 p=o.matrix_world@v.co;p.z=lookup[round(p.x,3),round(p.y,3)];v.co=o.matrix_world.inverted()@p
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Station_Gorge_Terrain.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'station_gorge.blend'))
(out/'terrain_grid.json').write_text(json.dumps({'vertices':vs}))
changed=[(x,y,z,nz) for (x,y,z),(_,_,nz) in zip(data['vertices'],vs) if abs(z-nz)>.00001]
assert all(-96<x<111 and -15<y<170 for x,y,_,_ in changed)
(out/'mesh_report.json').write_text(json.dumps({'changed':len(changed),'outside_mask_changes':0,'samples':[{'y':y,'z':lookup[-7,y]} for y in (0,7,12,20,30,40,60,90)]},indent=2))
