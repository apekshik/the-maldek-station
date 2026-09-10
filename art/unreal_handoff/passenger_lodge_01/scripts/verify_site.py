import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];b=json.loads((OUT/'before.json').read_text());o=b['origin']
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();lookup={a.get_name():a for a in actors}
changed=set(json.loads((OUT/'deck_install.json').read_text())['retired']+json.loads((OUT/'shell_install.json').read_text())['retired']+['VF10_Parking_Terrain','Landscape0'])
moves=json.loads((OUT/'vegetation_moves.json').read_text());moved={a['label'] for a in moves};errors=[];preserved=0
for r in b['actors']:
 a=lookup.get(r['name'])
 if not a:errors.append(r['label']+': missing');continue
 p=a.get_actor_location();rot=a.get_actor_rotation();scale=a.get_actor_scale3d()
 if r['label'] not in moved:
  for key,vals in [('location',[p.x,p.y,p.z]),('rotation',[rot.pitch,rot.yaw,rot.roll]),('scale',[scale.x,scale.y,scale.z])]:
   if max(abs(v-k) for v,k in zip(vals,r[key]))>.001:errors.append(r['label']+': '+key)
 if r['label'] not in changed:
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   old=next((v for v in r['components'] if v['name']==c.get_name()),None)
   if old and (c.static_mesh.get_path_name() if c.static_mesh else None)!=old['mesh']:errors.append(r['label']+': mesh')
  preserved+=1
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
terrain=[a for a in actors if a.get_actor_label() in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain];stairs=[]
for i in range(24):
 y=-14.42+i*.28+.14;top=(i+1)*4/24
 for x in [-7.7,-7.2,-6.7]:
  h=unreal.SystemLibrary.line_trace_single(w,wp(x,y,8),wp(x,y,-30),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  z=(h.to_tuple()[5].z-o[2])/100 if h and h.to_tuple()[0] else None
  stairs.append({'x':x,'y':y,'tread':i,'tread_top':top,'ground':z,'clear':z is not None and z<top-.07})
slots=[]
for kind in ['shell','deck']:
 for r in json.loads((OUT/(kind+'_exports.json')).read_text())['assets']:
  mesh=unreal.load_asset('/Game/MaldekRefinement/PassengerLodge/'+kind.capitalize()+'Pilot/Meshes/'+r['name']);assert mesh
  slots.append({'asset':r['name'],'source':r['materials'],'imported':[str(v.material_slot_name) for v in mesh.static_materials]})
original_unchanged=hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==b['map_sha256']
RESULT={'preserved_actor_components':preserved,'actor_errors':errors,'original_map_unchanged':original_unchanged,'stair_ground_probes':stairs,'stair_ground_clear':all(r['clear'] for r in stairs),'material_slots':slots}
(OUT/'site_verification.json').write_text(json.dumps(RESULT,indent=2))
assert original_unchanged and not errors
