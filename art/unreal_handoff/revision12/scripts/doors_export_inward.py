"""Inward-opening standard leaves: hinge hardware and stops on inside, front PUSH plaques."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/doors';sys.path.insert(0,str(out.parent/'scripts'));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/door_study_03/Maldek_Digital_Door_Variants.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE));bpy.context.scene.frame_set(1)
leaf=bpy.data.collections['01_Moving_leaf'];fixed=bpy.data.collections['02_Stationary_hardware'];bpy.context.view_layer.update()
for o in list(leaf.objects)+list(fixed.objects):
 if o.type not in ['MESH','FONT']:continue
 p=o.matrix_world.translation.copy();move=o in list(fixed.objects) or o.name.startswith('Moving_hinge') or (abs(p.x-.056)<.002 and p.y<-.03)
 if move:
  m=o.matrix_world.copy();m.translation.y=-p.y;o.matrix_world=m
bpy.data.objects['Pull_instruction'].data.body='PUSH TO OPEN';leaf.hide_render=False;leaf.hide_viewport=False;fixed.hide_render=False;fixed.hide_viewport=False
handoff=h.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx')
for name,code,title in [('Quarters','Q / 01','QUARTERS'),('Generator','G / 01','GENERATOR')]:
 bpy.data.objects['Door_ID'].data.body=code;bpy.data.objects['Door_ID_sub'].data.body=title;bpy.context.view_layer.update();handoff.deps=bpy.context.evaluated_depsgraph_get();handoff.chunk('SM_StationDoor_'+name+'InwardLeaf',[o for o in leaf.objects if o.name!='Vision_glass'],pivot=(.004,.035,0),role='thin')
for name,objects in [('InwardGlass',[bpy.data.objects['Vision_glass']]),('InwardFixed',list(fixed.objects))]:handoff.chunk('SM_StationDoor_'+name,objects,pivot=(.004,.035,0),role='thin')
(out/'inward_manifest.json').write_text(json.dumps({'source':str(h.SOURCE),'source_sha256':h.EXPECTED,'hinge_side':'interior','collision_center_y_cm':3.5,'chunks':handoff.chunks},indent=2))
