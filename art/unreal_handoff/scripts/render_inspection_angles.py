"""Additional clearly labelled fill-lit inspection renders; no level saves."""
from pathlib import Path
source=Path(__file__).with_name('render_review_angles.py').read_text()
insertion="""
for pitch,yaw,intensity in [(-40,35,2.0),(-35,160,.8),(-65,-90,.8)]:
 light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(),unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
 component=light.get_component_by_class(unreal.DirectionalLightComponent)
 component.set_mobility(unreal.ComponentMobility.MOVABLE)
 component.set_intensity(intensity)
 component.set_editor_property('cast_shadows',False)
shots=[(shots[i][0]+'_inspection',shots[i][1],shots[i][2]) for i in [0,1,4,5]]
"""
source=source.replace("state={'index':0",insertion+"\nstate={'index':0")
source=source.replace("'auto_exposure_bias',2.0","'auto_exposure_bias',0.0")
source=source.replace("'capture_report.json'","'capture_inspection_report.json'")
source=source.replace("'preview_exposure_bias_stops':2","'preview_exposure_bias_stops':0,'temporary_fill_lighting':True")
exec(compile(source,str(Path(__file__)), 'exec'))
