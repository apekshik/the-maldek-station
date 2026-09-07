import unreal,time,builtins
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';root='/Game/MaldekRefinement/R06';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
task=unreal.AssetImportTask();task.filename=str(out/'landscape_cliff.png');task.destination_path=root+'/HeightImport';task.automated=True;task.save=True;task.replace_existing=True;at.import_asset_tasks([task]);tex=lib.load_asset(root+'/HeightImport/landscape_cliff')
tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);lib.save_loaded_asset(tex)
m=lib.load_asset(root+'/HeightImport/M_HeightCopy') or at.create_asset('M_HeightCopy',root+'/HeightImport',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
s=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);s.texture=tex;s.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR;assert ml.connect_material_property(s,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ml.recompile_material(m);lib.save_loaded_asset(m)
rt=unreal.RenderingLibrary.create_render_target2d(world,4033,4033,unreal.TextureRenderTargetFormat.RTF_RGBA8);builtins.r06_height_rt=rt
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name()=='Landscape');assert land.landscape_export_heightmap_to_render_target(rt,True)
state={'when':time.monotonic()+12,'stage':0}
def tick(delta):
 if time.monotonic()<state['when']:return
 if state['stage']==0:
  unreal.RenderingLibrary.draw_material_to_render_target(world,rt,m);state.update(stage=1,when=time.monotonic()+4)
 else:
  unreal.RenderingLibrary.export_render_target(world,rt,str(out),'heightmap_roundtrip.png');unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)



