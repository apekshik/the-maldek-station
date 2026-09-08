"""Apply the bounded valley heightmap to the current map's owned landscape."""
import unreal,json,time,traceback,builtins
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';root='/Game/MaldekRefinement/R12/ForestRefine/HeightImport'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
land=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.Landscape));paths=unreal.StationMigrationLibrary.get_landscape_heightmap_paths(land);assert paths and all('/R12/Station_R12.' in p for p in paths)
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
t=unreal.AssetImportTask();t.filename=str(out/'landscape_valley.png');t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;at.import_asset_tasks([t]);tex=lib.load_asset(root+'/landscape_valley');assert tex
tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);lib.save_loaded_asset(tex)
m=lib.load_asset(root+'/M_HeightCopy') or at.create_asset('M_HeightCopy',root,unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
n=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);n.texture=tex;n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR;ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ml.recompile_material(m);lib.save_loaded_asset(m)
rt=unreal.RenderingLibrary.create_render_target2d(w,4033,4033,unreal.TextureRenderTargetFormat.RTF_RGBA8);builtins.forest_height_rt=rt
s={'stage':0,'next':time.monotonic()+12,'busy':False}
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  if s['stage']==0:
   unreal.RenderingLibrary.draw_material_to_render_target(w,rt,m);s.update(stage=1,next=time.monotonic()+4);return
  assert land.landscape_import_heightmap_from_render_target(rt,True);assert ls.save_current_level();s.update(success=True,saved=True);(out/'landscape_applied.json').write_text(json.dumps(s));unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  s['error']=traceback.format_exc();(out/'landscape_applied.json').write_text(json.dumps(s));unreal.unregister_slate_post_tick_callback(handle)
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True,'owned_components':len(paths)}
