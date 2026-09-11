import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Office.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
a=json.loads((P/'assembly.json').read_text());v=json.loads((P/'verification.json').read_text());recipes=[]
prefixes=['Door_leaf','Drawer_bottom','Drawer_side','Drawer_front_back','Shutter_panel','Secure_door_stile','Secure_door_rail','Tray_base','Tray_side','Tray_lip','Counter_top','Counter_end','Counter_public_apron','Shelf_','Rack_upright','Secure_side','Secure_back','Secure_shelf','Trolley_deck']
for o in bpy.data.collections['WSP_ASSETS'].objects:
 if o.type!='MESH' or not any(o.name.startswith('WSP_'+p) for p in prefixes):continue
 pivot=o.parent
 transform=(pivot.matrix_world.inverted()@o.matrix_world) if pivot else o.matrix_world
 recipes.append({'source_mesh':o.name,'shape':'box','attach_to':pivot.name if pivot else 'assembly_origin','centre_in_attach_space':list(transform.translation),'rotation_quaternion_wxyz':list(transform.to_quaternion()),'dimensions_m':list(o.dimensions),'purpose':'Preliminary physical blocking; retain actual empty structural volumes'})
out={'units':'metres','status':'Blender-authored recipes, engine collision not built or tested','boxes':recipes,'sweeps':v['sweeps'],'excluded':'Small hinge barrels, latches, tags, scale ticks, loose pencils, wire strands and text remain visual/aimable; do not box-fill open shelving or wire cabinet. Secure door frame boxes do not prevent tiny items passing wire; add a thin interaction-only plane for gameplay if required.'}
(P/'collision.json').write_text(json.dumps(out,indent=2));a['collision_recipe']='collision.json';a['geometry_inventory']='verification.json:inventory';a['mechanism_sweeps']='collision.json:sweeps';(P/'assembly.json').write_text(json.dumps(a,indent=2));print('COLLISION_RECIPES',len(recipes))
