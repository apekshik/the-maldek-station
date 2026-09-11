"""Final metadata only; run after review and verification have completed."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
v=json.loads((P/'verification.json').read_text()); assert v['passed'], 'Verification must pass before delivery'
assert json.loads((P/'pose_audit.json').read_text())['passed'], 'All three named poses must pass geometry audit'
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Editable.blend'))
S=bpy.context.scene; C=bpy.data.collections['WSR_ASSETS']; a=json.loads((P/'assembly.json').read_text())
a['objects']={o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'rest_local_matrix':[list(r) for r in o.matrix_local],'dimensions_m':list(o.dimensions),'material_slots':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []} for o in C.objects}
a['blind']={'roller_pivot':[5.735,3.9,2.10],'mesh':'WSR_Privacy_blind_fabric','shape_key':'Lowered','raised_bottom_m':1.776,'lowered_bottom_m':1.10}
a['stretcher_lock_slides']={o.name:{'axis':o['travel_axis'],'release_travel_m':o['release_travel_m'],'parent':o.parent.name,'released_frame':1,'locked_frame':40} for o in C.objects if 'travel_axis' in o}
a['mechanism_sweeps_file']='asset_geometry.json'
a['rough_openings_local']={'door':{'x':[5.8,6.0],'y':[1.2,2.9],'z':[0,2.35]},'window':{'x':[5.8,6.0],'y':[3.35,4.45],'z':[1.0,2.05]}}
a['door_clear_ray_verified_m']=[1.5,2.15]
a['surface_patch_ledger']=[]
a['provenance']={'geometry':'Original generated mesh construction; no externally sourced meshes','textures':'None; no external dependencies to pack','materials':'Original procedural Blender graphs; baking and LOD/export work remains','lettering':'Editable Blender font data and original wording; convert export copies'}
a['interaction_anchors']={o.name:{'height_above_floor_m':o['control_height_m'],'positive_Y_approach':list(o['approach_local_positive_Y']),'local_location':list(o.location),'local_rotation_radians':list(o.rotation_euler)} for o in C.objects if 'control_height_m' in o}
a['material_slots_by_object']={o.name:[m.name for m in o.data.materials] for o in C.objects if o.type in ['MESH','FONT']}
(P/'assembly.json').write_text(json.dumps(a,indent=2))
geo=json.loads((P/'asset_geometry.json').read_text())
recipe={'status':'Future exporter guidance; not authored UCX or verified engine collision','units':'metres local WSR space','exclude':['text','cords','hinge barrels','handles','small controls','grille bars','glass unless engine design requires blocking'],'door_leaves':{},'fixed_panel_candidates':{},'dynamic':'Build collision in each actual pivot coordinate frame; never use the entire swept volume as moving collision.'}
for o in C.objects:
 if o.type!='MESH':continue
 if '_leaf' in o.name:recipe['door_leaves'][o.name]={'parent_pivot':o.parent.name,'local_matrix':[list(r) for r in o.matrix_local],'box_dimensions_m':list(o.dimensions)}
 elif any(s in o.name for s in ['cupboard_side','cupboard_back','Blanket_shelf','Cot_pad','Chair_seat','Heater_housing','Aid_cabinet_side','Aid_cabinet_back']):recipe['fixed_panel_candidates'][o.name]=geo['objects'][o.name]['bounds']
(P/'collision_recipe.json').write_text(json.dumps(recipe,indent=2))
previews=sorted((P/'previews').glob('*.png')); assert len(previews)>=11
files=[p for p in P.rglob('*') if p.is_file() and p.suffix.lower() in ['.blend','.png','.svg','.py','.json','.md'] and p.name!='delivery.json']
delivery={'package':'WSR_ASSETS','editable_blend':'Maldek_Rescue_Hut_Editable.blend','fitted_blend':'Maldek_Rescue_Hut_Fitted_Review.blend','verification_passed':v['passed'],'review_images':[p.relative_to(P).as_posix() for p in previews],'source_master_sha256':hashlib.sha256((P.parent/'west_services_01/Maldek_West_Services_Blockout.blend').read_bytes()).hexdigest(),'sha256':{p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
assert delivery['source_master_sha256']=='54bb3f1e54a6c84ebd1b90c5664e6e7b328be6e6139bac0f6fd9f49ea630b6aa'
(P/'delivery.json').write_text(json.dumps(delivery,indent=2));print('DELIVERY FINALIZED',len(files),'files;',len(previews),'images')

