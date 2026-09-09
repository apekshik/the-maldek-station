import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
s=bpy.context.scene
checks={}
group=bpy.data.collections['NS01_Stationary_sign']
checks['stationary_root']=bpy.data.objects['NS01_Mount_origin'].parent is None
states={'BOARD':1,'ARRIVING':49,'DEPART':97,'AWAY':145}
strengths={}
for state,frame in states.items():
 s.frame_set(frame)
 strengths[state]={name:bpy.data.materials['NS01_Circuit_'+name].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for name in states}
checks['one_lit_circuit_per_state']=all([name for name,v in values.items() if v>1]==[state] for state,values in strengths.items())
bad=[];count=0
deps=bpy.context.evaluated_depsgraph_get()
for o in group.objects:
 if o.type!='MESH':continue
 count+=1;ev=o.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
 if any(not e.is_manifold for e in bm.edges):bad.append(o.name)
 bm.free();ev.to_mesh_clear()
checks['closed_meshes']=not bad
checks['tube_cap_repair_saved']=not any(o.type=='CURVE' for o in group.objects)
electrodes=[tuple(round(v,6) for v in o.location) for o in group.objects if o.name.startswith('NS01_Electrode_')]
checks['unique_electrode_surfaces']=len(electrodes)==len(set(electrodes))
corners=[o.matrix_world@Vector(c) for o in group.objects if o.type=='MESH' for c in o.bound_box]
checks['wide_landscape_panel']=(max(p.x for p in corners)-min(p.x for p in corners))>1.7*(max(p.z for p in corners)-min(p.z for p in corners))
checks['no_pole']=not any(o.name in ['NS01_Post','NS01_Rear_spine','NS01_Foot_flange'] for o in group.objects)
checks['previews_exist']=all((out/'previews'/(name+'.png')).exists() for name in ['01_BOARD','02_ARRIVING','03_DEPART','04_AWAY','05_Placement','06_Rear'])
report={'success':all(checks.values()),'checks':checks,'mesh_objects':count,'nonmanifold':bad,'circuit_strengths':strengths,'minimum_sign_world_x_m':min(p.x for p in corners),'bounds_world_m':[[min(p[i] for p in corners),max(p[i] for p in corners)] for i in range(3)],'integration':'Blender model verified before Unreal reimport'}
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
assert report['success'],report
