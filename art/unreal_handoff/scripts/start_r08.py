import unreal,json,runpy
from pathlib import Path
scripts=Path(__file__).resolve().parent
out=scripts.parent/'revision08'
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
root='/Game/MaldekRefinement/R08/BlockOut_R08'
if unreal.EditorAssetLibrary.does_asset_exist(root): assert levels.load_level(root)
else: assert levels.new_level_from_template(root,'/Game/MaldekRefinement/R07/BlockOut_R07')
r=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.PointLightComponent):
  p=a.get_actor_location()
  r.append({'label':a.get_actor_label(),'class':c.get_class().get_name(),'position':[p.x,p.y,p.z],'intensity':c.get_editor_property('intensity'),'units':str(c.get_editor_property('intensity_units')),'attenuation':c.get_editor_property('attenuation_radius')})
(out/'existing_lights.json').write_text(json.dumps(r,indent=2))
assert levels.save_current_level()
runpy.run_path(str(scripts/'review_session.py'))
