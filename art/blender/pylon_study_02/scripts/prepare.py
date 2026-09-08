from pathlib import Path
root=Path('art/blender');s=(root/'pylon_study_01/scripts/build.py').read_text();p=root/'pylon_study_02/scripts/build.py'
s=s.replace("Modern twin-tube Maldek pylon.","Weathered single-lane central portal Maldek pylon.")
s=s.replace("paint=material('Pylon_Satin_Silver',(.47,.56,.59),.45,.44)","paint=material('Pylon_Faded_Grey_Green',(.26,.31,.28),.12,.78)")
s=s.replace("(.045,.065,.073),.72,.33)","(.055,.07,.065),.35,.79)").replace("(.38,.43,.45),.85,.28)","(.27,.29,.265),.48,.72)")
s=s.replace("(.88,.40,.06),.25,.37)","(.48,.30,.085),.06,.83)")
s=s.replace('H=42.;shaft_top=40.6','H=42.;shaft_top=43.55')
s=s.replace('range(134)','range(144)').replace('(x1+dx,.92,42.6)','(x1+dx,.92,44.6)').replace('(x1,.94,41.65)','(x1,.94,43.65)')
a=s.index('# Transverse tube brace');b=s.index('# Export specification.')
head='''# A central passenger lane passes THROUGH the open twin-leg portal.
# All transverse structure is above the rope. No beam crosses the cabin envelope.
box('Portal_overhead_girder',(0,0,44.05),(7.7,1.45,1.0),dark,.09)
box('Portal_top_flange',(0,0,44.59),(7.9,1.60,.08),galv,.025)
for side in [-1,1]:
 tube('Portal_knee_brace',(side*3.3,0,40.1),(side*1.95,0,43.55),.23,.20,paint)
 # Down-facing discrete inspection fixtures and head marker pods.
 box('Maintenance_light_housing',(side*2.45,-.76,43.82),(.45,.16,.16),dark,.035)
 tube('Beacon_base',(side*3.35,0,44.65),(side*3.35,0,44.81),.16,mat=dark)
 tube('Red_marker_lens',(side*3.35,0,44.81),(side*3.35,0,45.05),.12,mat=red)
# One central 12-sheave support assembly. Hanger clearance is reserved on +X side.
x=0.
for y in [-2.1,2.1]:
 box('Central_suspension_drop',(-.58,y,42.58),(.20,.24,2.14),dark,.035)
 box('Head_longitudinal_carrier',(-.58,0,43.55),(.36,5.0,.28),galv,.035)
box('Main_rocker',(-.37,0,41.4),(.15,5.6,.34),galv,.04)
rod('Main_rocker_pin',(-.75,0,41.45),(-.22,0,41.45),.16,dark)
for center in [-2.1,2.1]:
 box('Secondary_rocker',(-.26,center,41.78),(.12,3.8,.21),galv,.03)
 for offset in [-1.60,-.96,-.32,.32,.96,1.60]:
  y=center+offset;z=42.02
  tube('Rubber_sheave',(-.075,y,z),(.075,y,z),.275,mat=rubber,verts=40)
  for dx in [-.097,.097]:
   tube('Sheave_side_disc',(dx-.017,y,z),(dx+.017,y,z),.293,mat=galv,verts=40)
   tube('Sheave_hub',(dx-.045,y,z),(dx+.045,y,z),.105,mat=dark,verts=24)
  rod('Sheave_axle',(-.35,y,z),(.17,y,z),.060,galv)
# Single side service deck, reached by the left shaft ladder.
cx=-1.50
for y in [-3.8+i*.20 for i in range(39)]:box('Walkway_grating',(cx,y,42.55),(.90,.045,.065),galv,.004)
for dx in [-.46,.46]:
 rod('Catwalk_stringer',(cx+dx,-3.9,42.44),(cx+dx,3.9,42.44),.048,dark)
 for y in [-3.85,-1.925,0,1.925,3.85]:rod('Guard_post',(cx+dx,y,42.55),(cx+dx,y,43.64),.025)
 for z in [43.08,43.64]:rod('Guard_rail',(cx+dx,-3.85,z),(cx+dx,3.85,z),.025)
for y in [-3.85,3.85]:
 for z in [43.08,43.64]:rod('Catwalk_end_guard',(cx-.46,y,z),(cx+.46,y,z),.025)
for y in [-2.9,2.9]:
 tube('Deck_hanger',(-1.5,y,42.40),(-1.5,y,43.52),.055,mat=dark)
for x in [-3.1+i*.13 for i in range(10)]:box('Ladder_transfer_grating',(x,1.18,42.55),(.04,.72,.065),galv,.004)
# Bare return-rope rollers ABOVE the head: no second cabin lane or hanger fittings.
for y in [-.95,-.32,.32,.95]:
 box('Return_roller_mount',(-2.35,y,44.72),(.42,.18,.18),dark,.02)
 tube('Return_rope_roller',(-2.46,y,44.90),(-2.24,y,44.90),.20,mat=rubber,verts=32)
 for dx in [-2.48,-2.22]:tube('Return_roller_flange',(dx-.012,y,44.90),(dx+.012,y,44.90),.22,mat=galv,verts=32)
for y in [-3.65,3.65]:
 box('Central_rope_sensor',(-.30,y,42.40),(.18,.19,.14),amber,.015)
# Finish weathering is evaluated in a shared world-coordinate frame, so it survives joining.
weather_origin=bpy.data.objects.new('Weathering_coordinate_frame',None);scene.collection.objects.link(weather_origin)
def weather(m,base,shade,metal,rough,amount):
 n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
 tc=n.new('ShaderNodeTexCoord');tc.object=weather_origin
 broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=1.25;broad.inputs['Detail'].default_value=4;l.new(tc.outputs['Object'],broad.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(*shade,1);ramp.color_ramp.elements[1].position=.77;ramp.color_ramp.elements[1].color=(*base,1);l.new(broad.outputs['Fac'],ramp.inputs[0])
 mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(13,13,.7);l.new(tc.outputs['Object'],mapping.inputs[0])
 streak=n.new('ShaderNodeTexNoise');streak.inputs['Scale'].default_value=1;streak.inputs['Detail'].default_value=3;l.new(mapping.outputs[0],streak.inputs['Vector'])
 mask=n.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.60;mask.color_ramp.elements[1].position=.76;mask.color_ramp.elements[1].color=(amount,amount,amount,1);l.new(streak.outputs['Fac'],mask.inputs[0])
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.17,.065,.022,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Base Color'])
 bs.inputs['Metallic'].default_value=metal
 rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=rough;rr.inputs['To Max'].default_value=.94;l.new(broad.outputs['Fac'],rr.inputs['Value']);l.new(rr.outputs[0],bs.inputs['Roughness'])
 fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=35;fine.inputs['Detail'].default_value=2;l.new(tc.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.007;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
weather(paint,(.30,.34,.30),(.13,.17,.145),.10,.74,.55)
weather(dark,(.095,.115,.10),(.028,.039,.032),.22,.76,.65)
weather(galv,(.40,.42,.37),(.13,.16,.14),.40,.68,.7)
weather(amber,(.54,.35,.095),(.25,.18,.07),.03,.8,.35)
# Dedicated collar patina concentrates corrosion at joints rather than coating whole shafts.
rust=material('Pylon_Joint_Patina',(.19,.072,.021),.1,.91);weather(rust,(.24,.095,.032),(.06,.035,.018),.1,.86,.3)
for o in list(parts.objects):
 if any(t in o.name for t in ['flange_ring','flange_bolt','Anchor_gusset']):
  o.data.materials.clear();o.data.materials.append(rust)
'''
s=s[:a]+head+s[b:]
s=s.replace("for x in [-7.1,7.1]:rod('STUDY_cable',(x,-32,42.327),(x,32,42.327),.032,dark)","rod('STUDY_central_passenger_rope',(0,-32,42.327),(0,32,42.327),.032,dark)\nrod('STUDY_bare_return_rope',(-2.35,-32,45.132),(-2.35,32,45.132),.032,dark)")
s=s.replace("'Maldek modern twin tubular pylon / 42 m study / cylinder shafts and 12-sheave trains'","'Maldek single central passenger lane / overhead portal / weathered finish'")
s=s.replace("'design_height_m':43.63", "'design_height_m':45.12").replace("'head_rope_gauge_m':14.2", "'passenger_lanes':1,'passenger_rope_x_m':0,'bare_return_rope_x_m':-2.35")
s=s.replace('Maldek_Modern_Twin_Pylon','Maldek_Weathered_Central_Pylon').replace('SM_Maldek_Twin_Pylon_42m','SM_Maldek_Central_Pylon')
s=s.replace("'02_crosshead':camera('CAM_02_Crosshead',(23,-29,49),(0,0,41.2),56)","'02_crosshead':camera('CAM_02_Crosshead',(15,-23,46),(0,0,42),57)")
s=s.replace("'04_night':camera", "'04_front_clearance':camera('CAM_04_Front',(0,-29,40.8),(0,0,40.8),55),\n '05_night':camera")
s=s.replace("if name=='04_night':", "if name=='05_night':")
s=s.replace("elif name=='03_base_detail':", "elif name in ['03_base_detail','04_front_clearance']:")
s=s.replace("print('PYLON_STUDY_COMPLETE'", "print('CENTRAL_PYLON_STUDY_COMPLETE'")
# Save default viewport framing for the reusable Blender asset.
s=s.replace("bpy.ops.wm.save_as_mainfile(filepath=str(OUT/", "for screen in bpy.data.screens:\n for area in screen.areas:\n  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'\nbpy.ops.wm.save_as_mainfile(filepath=str(OUT/",1)
p.write_text(s)
