"""Install the local panel; does not transmit credentials or generate previews."""
import bpy,addon_utils,shutil
from pathlib import Path
source=Path(__file__).resolve().parent/'blender_addon'/'maldek_h3'
target=Path(bpy.utils.user_resource('SCRIPTS',path='addons',create=True))/'maldek_h3'
shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
bpy.utils.refresh_script_paths()
addon_utils.enable('maldek_h3',default_set=True,persistent=True)
assert 'maldek_h3' in bpy.context.preferences.addons
bpy.ops.wm.save_userpref()
print('MALDEK_ADDON_INSTALLED',target)
