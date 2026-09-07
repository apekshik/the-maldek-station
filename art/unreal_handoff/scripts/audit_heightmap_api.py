import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06'
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();land=next(a for a in a if a.get_class().get_name()=='Landscape')
r={n:getattr(land,n).__doc__ for n in ['landscape_export_heightmap_to_render_target','landscape_import_heightmap_from_render_target']}
r['render_api']={n:getattr(unreal.RenderingLibrary,n).__doc__ for n in ['create_render_target2d','export_render_target','draw_material_to_render_target','import_file_as_texture2d']}
r['landscape']={'location':str(land.get_actor_location()),'scale':str(land.get_actor_scale3d()),'components':[]}
for c in land.get_components_by_class(unreal.LandscapeComponent):
 d={}
 for p in ['section_base_x','section_base_y','component_size_quads','heightmap_texture']:
  try:d[p]=str(c.get_editor_property(p))
  except:d[p]='unavailable'
 r['landscape']['components'].append(d)
(out/'heightmap_api.json').write_text(json.dumps(r,indent=2))
