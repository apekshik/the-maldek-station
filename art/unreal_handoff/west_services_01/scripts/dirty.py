import unreal
RESULT={'content':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'maps':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
