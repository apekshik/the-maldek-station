"""Idempotent R12 pawn tuning and local office/bridge practical fixtures."""
import json, math, unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1]; out=b/'sensory_refine'; out.mkdir(exist_ok=True)
lib=unreal.EditorAssetLibrary; aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p): return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
def transform(a): return (a.get_actor_location().to_tuple(),a.get_actor_rotation().to_tuple(),a.get_actor_scale3d().to_tuple())
preserved={k:transform(a) for k,a in actors.items() if not k.startswith('R12_Sensory_')}
root='/Game/MaldekRefinement/R12/Sensory'
steel=lib.load_asset('/Game/MaldekRefinement/R12/GondolaMarkers/M_Marker_Base')
assert steel
def material(name,base,emissive):
 path=root+'/'+name
 m=lib.load_asset(path)
 if not m:
  m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,root,unreal.Material,unreal.MaterialFactoryNew())
  ml=unreal.MaterialEditingLibrary
  for value,prop in [(base,unreal.MaterialProperty.MP_BASE_COLOR),(emissive,unreal.MaterialProperty.MP_EMISSIVE_COLOR)]:
   n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
   n.set_editor_property('constant',unreal.LinearColor(*value,1));ml.connect_material_property(n,'',prop)
  ml.recompile_material(m);lib.save_loaded_asset(m)
 return m
panel=material('M_Office_Diffuser',(.72,.68,.54),(1.2,.94,.57))
# Same saturated red as the gondola lamps, with substantially lower emission.
red=material('M_Bridge_Dim_Red',(.15,.001,.0003),(.45,.00135,.00045))
made=[]
def body(name,p,size,mat,shape='Cube'):
 label='R12_Sensory_'+name
 a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(p))
 a.set_actor_label(label);a.set_folder_path('R12/Infrastructure/SensoryFixtures')
 a.set_actor_location(wp(p),False,True);a.set_actor_scale3d(unreal.Vector(*size))
 c=a.static_mesh_component;c.set_static_mesh(lib.load_asset('/Engine/BasicShapes/'+shape))
 c.set_material(0,mat);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_cast_shadow(False)
 made.append({'label':label,'position_m':p,'size_m':size});return a
def light(name,p,cls):
 label='R12_Sensory_'+name;a=actors.get(label) or aa.spawn_actor_from_class(cls,wp(p))
 a.set_actor_label(label);a.set_folder_path('R12/Infrastructure/SensoryFixtures');a.set_actor_location(wp(p),False,True)
 c=a.get_component_by_class(unreal.LightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS)
 c.set_volumetric_scattering_intensity(0)
 made.append({'label':label,'position_m':p});return a,c
# Adjacent office/waiting hall: ceiling underside z=7.15 m, floor z=4 m.
# Housing ends at 7.14; diffuser sits entirely below it with a 2 mm concealed gap.
for i,x in enumerate([-11.0,-15.0]):
 y=-3.0
 body('Office_%d_Housing'%i,[x,y,7.10],[1.12,.32,.08],steel)
 body('Office_%d_Panel'%i,[x,y,7.045],[1.04,.24,.026],panel)
 a,c=light('Office_%d_Light'%i,[x,y,7.015],unreal.RectLight)
 a.set_actor_rotation(unreal.Rotator(pitch=-90),False)
 c.set_intensity(.85);c.set_editor_property('attenuation_radius',520)
 c.set_editor_property('source_width',104);c.set_editor_property('source_height',24)
 c.set_editor_property('use_temperature',True);c.set_temperature(3500);c.set_cast_shadows(True)
# Caps stand above the existing crosshead (top 14.11 m), centered over its pillars.
for i,x in enumerate([11.0,13.0]):
 body('Bridge_%d_Base'%i,[x,7.5,14.135],[.20,.20,.05],steel,'Cylinder')
 body('Bridge_%d_RedLens'%i,[x,7.5,14.195],[.12,.12,.066],red,'Cylinder')
 a,c=light('Bridge_%d_Spill'%i,[x,7.5,14.21],unreal.PointLight)
 c.set_intensity(.003);c.set_editor_property('attenuation_radius',45)
 c.set_light_color(unreal.LinearColor(1,.003,.001,1));c.set_cast_shadows(False);c.set_indirect_lighting_intensity(0)
pawn=unreal.get_default_object(w.get_world_settings().default_game_mode).default_pawn_class
bp=lib.load_asset(pawn.get_path_name().split('.')[0]);cdo=unreal.get_default_object(pawn)
foot=cdo.get_component_by_class(unreal.SurfaceFootstepComponent)
foot.set_editor_property('volume',3.5)
camera=cdo.get_component_by_class(unreal.StationPlayerPresentationComponent)
settings={'head_bob_scale':1.5,'idle_sway_scale':5.0,'walk_sway_cm':1.8,'run_sway_cm':3.0}
for k,v in settings.items():camera.set_editor_property(k,v)
unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False)
for k,v in preserved.items():assert transform(actors[k])==v,k
assert ls.save_current_level()
errors=list(unreal.StationMigrationLibrary.validate_material_shaders([panel,red]));assert not errors,errors
RESULT={'success':True,'pawn':bp.get_path_name(),'foot_volume':3.5,'camera':settings,'fixtures':made,
 'existing_actor_transforms_preserved':len(preserved),'global_lighting_changed':False,
 'office_headroom_m':3.032,'bridge_red_emission_vs_gondola':.15}
(out/'setup.json').write_text(json.dumps(RESULT,indent=2))
