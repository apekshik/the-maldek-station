import bpy,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/doors';base=root/'art/unreal_handoff/revision13';sys.path.insert(0,str(out.parent/'scripts'));import mesh_handoff as h
h.OUT=out;h.SOURCE=root/'art/blender/visual_fidelity_09/Maldek_Service_Apron_Refinement.blend';h.EXPECTED=hashlib.sha256(h.SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(h.SOURCE),load_ui=False)
orig=h.collision_kind
def ck(o):
 n=o.name.lower()
 if 'connected_service_road' in n:return 'surface_prisms'
 if any(t in n for t in ['concrete_panel','hall_foundation','workshop_floor','inertia_plinth']):return 'floor'
 if any(t in n for t in ['insulated_wall_core','opening_jamb','opening_header','open_service_door','switchgear_cabinet','day_tank','crankcase','alternator_body','radiator_frame','dished_horizontal_shell','column','bund_side','bund_end','stem_foundation']):return 'solid'
 return orig(o)
h.collision_kind=ck;handoff=h.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx');manifest=json.loads((base/'handoff_manifest.json').read_text());row=next(r for r in manifest['chunks'] if 'VF08_Open_service_door' in r['sources'])
removed=[n for n in row['sources'] if n.startswith(('VF08_Open_service_door','VF08_Door_hinge','VF08_Door_push_bar'))];objects=[bpy.data.objects[n] for n in row['sources'] if n not in removed]
new=handoff.chunk('SM_StationDoor_ServiceShell',objects,pivot=row['pivot'],role=row['role'],exposure='Exterior')
oldboxes=[c for c in row['collision_boxes'] if c['source'] not in removed]
assert new['collision_boxes']==oldboxes,'Unexpected non-door collision change'
(out/'service_shell_manifest.json').write_text(json.dumps({'source_asset':row['name'],'removed':removed,'chunk':new,'non_door_collision_preserved':True},indent=2))
# Measured current doorway evidence.
from mathutils import Vector
rows=[]
for o in bpy.data.objects:
 if o.name.startswith(('VF08_Flush_threshold','VF08_Opening_header')):
  pts=[o.matrix_world@Vector(v) for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box];rows.append({'name':o.name,'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]})
(out/'current_service_openings.json').write_text(json.dumps(rows,indent=2))
