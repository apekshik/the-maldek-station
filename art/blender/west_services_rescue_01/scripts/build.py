"""Original metre-scale rescue fittings. Run with Blender 5 background --python."""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parents[1]; (P/'previews').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.name='WSR_Editable_Local'; S.unit_settings.system='METRIC'
C=bpy.data.collections.new('WSR_ASSETS'); S.collection.children.link(C)
def link(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o); return o
def material(n,c,metal=0,rough=.5,grain=False):
 m=bpy.data.materials.new('WSR_'+n); m.diffuse_color=(*c,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
 if grain:
  ns=m.node_tree.nodes; ls=m.node_tree.links; tex=ns.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=6; tex.inputs['Detail'].default_value=3
  coord=ns.new('ShaderNodeTexCoord'); vec=ns.new('ShaderNodeVectorMath'); vec.operation='MULTIPLY'; vec.inputs[1].default_value=(4,4,65)
  ls.new(coord.outputs['Generated'],vec.inputs[0]); ls.new(vec.outputs[0],tex.inputs['Vector'])
  ramp=ns.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(*(v*.65 for v in c),1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(*c,1); ls.new(tex.outputs['Fac'],ramp.inputs[0]); ls.new(ramp.outputs[0],bs.inputs['Base Color'])
  bump=ns.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.001; ls.new(tex.outputs['Fac'],bump.inputs['Height']); ls.new(bump.outputs[0],bs.inputs['Normal'])
 m['provenance']='Original procedural Blender material; bake before engine export.'; return m
pine=material('Honey_pine',(.43,.245,.105),grain=True); cream=material('Warm_cream_enamel',(.72,.68,.53),rough=.38)
petrol=material('Petrol_enamel',(.045,.19,.19),.25,.36); steel=material('Galvanized_steel',(.43,.49,.49),.78,.29)
rubber=material('Graphite_rubber',(.024,.03,.026),rough=.72); olive=material('Olive_wool',(.22,.27,.12),grain=True)
orange=material('Muted_rescue_canvas',(.64,.19,.046),grain=True); linen=material('Cot_canvas',(.65,.61,.45),grain=True)
paper=material('Checklist_paper',(.82,.8,.66)); ink=material('Printed_ink',(.025,.065,.052)); green=material('Aid_green',(.08,.28,.17))
glass=material('Window_glass',(.7,.83,.8),rough=.12); bs=glass.node_tree.nodes.get('Principled BSDF'); bs.inputs['Transmission Weight'].default_value=.78; bs.inputs['IOR'].default_value=1.45
def box(n,p,d,m,b=.007):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=link(bpy.context.object); o.name='WSR_'+n; o.dimensions=d; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if b:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL'); mod.width=min(b,min(d)*.24); mod.segments=3
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(b-a).length,location=(a+b)/2); o=link(bpy.context.object); o.name='WSR_'+n; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); mod=o.modifiers.new('Edge radius','BEVEL'); mod.width=min(.002,r*.2); mod.segments=2; return o
def empty(n,p=(0,0,0)):
 o=bpy.data.objects.new(n,None); C.objects.link(o); o.location=p; o.empty_display_type='ARROWS'; o.empty_display_size=.15; return o
def parent(o,p):
 bpy.context.view_layer.update(); w=o.matrix_world.copy(); o.parent=p; o.matrix_world=w
def label(n,text,p,size,m=ink,face='south'):
 cu=bpy.data.curves.new(n,'FONT'); cu.body=text; cu.size=size; cu.extrude=.0005; cu.space_line=1.2
 o=bpy.data.objects.new('WSR_'+n,cu); C.objects.link(o); o.location=p; o.data.materials.append(m)
 # text local +X right, +Y up, normal +Z
 o.rotation_euler={'south':(math.pi/2,0,0),'west':(math.pi/2,0,math.pi/2),'east':(math.pi/2,0,-math.pi/2)}[face]; return o
def screws(n,points,axis='X'):
 for i,p in enumerate(points):
  a=Vector(p); b=a.copy(); b['XYZ'.index(axis)]+=.006; rod(n+str(i),a,b,.007,steel)
def mechanism(n,p,axis,angle):
 o=empty(n,p); o['axis']=axis; o['closed_degrees']=0.; o['open_degrees']=angle; return o
def keyrot(o,axis,a,frame):
 o.rotation_euler[axis]=math.radians(a); o.keyframe_insert('rotation_euler',frame=frame)
# East door: shell bounds local X 5.8..6.0. Frame alone owns reveals.
for y in [1.242,2.858]: box('Door_jamb',(5.9,y,1.14),(.216,.076,2.28),petrol)
box('Door_head',(5.9,2.05,2.309),(.216,1.54,.074),petrol)
box('Threshold',(5.9,2.05,.006),(.27,1.54,.012),steel,.002)
for y in [1.215,2.885]: box('Concealed_jamb_packing',(5.91,y,1.13),(.16,.029,2.25),rubber,.001)
for y in [1.276,2.824]: box('Door_seal',(5.784,y,1.137),(.05,.008,2.258),rubber,.001)
box('Head_seal',(5.784,2.05,2.276),(.05,1.532,.008),rubber,.001)
doors=[]
for side,y,sgn in [('Active',1.28,1),('Passive',2.82,-1)]:
 root=mechanism('WSR_Door_'+side+'_HINGE',(5.768,y,0),'Z',90*sgn); doors.append(root)
 before=set(C.objects)
 cy=y+sgn*.374
 box('Door_'+side+'_leaf',(5.741,cy,1.149),(.045,.788,2.262),pine)
 box('Door_'+side+'_bottom_weatherseal',(5.741,cy,.015),(.040,.788,.006),rubber,.001)
 if side=='Active': box('Meeting_astragal',(5.767,2.051,1.149),(.008,.020,2.262),rubber,.001)
 for z in [.18,1.98]: box('Door_'+side+'_rail',(5.769,cy,z),(.015,.686,.12),petrol)
 box('Door_'+side+'_kickplate',(5.769,cy,.42),(.012,.686,.28),steel,.003)
 for dx in [5.715,5.767]:
  box('Door_'+side+'_latch_plate',(dx,y+sgn*.64,1.06),(.009,.045,.17),steel,.002)
  rod('Door_'+side+'_handle_spindle',(dx,y+sgn*.64,1.07),(dx+(.025 if dx>5.74 else -.025),y+sgn*.64,1.07),.012,steel)
  rod('Door_'+side+'_lever',(dx+(.025 if dx>5.74 else -.025),y+sgn*.64,1.07),(dx+(.025 if dx>5.74 else -.025),y+sgn*.52,1.07),.013,steel)
 for z in [.25,1.13,2.02]: rod('Door_'+side+'_hinge_barrel',(5.768,y,z-.07),(5.768,y,z+.07),.015,steel)
 if side=='Passive':
  for z in [.15,2.09]: rod('Passive_flush_bolt',(5.71,2.10,z-.06),(5.71,2.10,z+.06),.009,steel)
 for o in set(C.objects)-before: parent(o,root)
 keyrot(root,2,0,1); keyrot(root,2,90*sgn,40); keyrot(root,2,90*sgn,80)
 # Wall magnetic hold-open catch, off transfer zone.
 box('Hold_open_'+side,(5.07,y-sgn*.12,.12),(.07,.07,.12),rubber)
# Window separate panes, reveals, blind lifted above eye level.
for y in [3.387,4.413]: box('Window_jamb',(5.9,y,1.525),(.216,.066,1.042),cream)
for z in [1.037,2.013]: box('Window_rail',(5.9,3.9,z),(.216,.96,.066),cream)
box('Window_glazing',(5.915,3.9,1.525),(.008,.96,.91),glass,.001)
box('Window_sill',(5.765,3.9,1.012),(.3,1.18,.024),pine,.005)
blind=mechanism('WSR_Privacy_blind_ROLL',(5.735,3.9,2.10),'Y',360)
rod('Blind_roller',(5.735,3.38,2.10),(5.735,4.42,2.10),.033,cream)
blindcloth=box('Privacy_blind_fabric',(5.735,3.9,1.926),(.012,1.01,.30),linen,.001)
blindcloth['raised_bottom_m']=1.776; blindcloth['lowered_bottom_m']=1.10
blindcloth.shape_key_add(name='Raised'); k=blindcloth.shape_key_add(name='Lowered')
k.value=0.0
for v in k.data:
 if v.co.z<0: v.co.z-=.676
rod('Blind_pull',(5.72,4.47,1.4),(5.72,4.47,2.08),.003,rubber)
box('Blind_cleat',(5.72,4.50,1.38),(.045,.03,.06),cream)
# Simple west-central cot, clear below and accessible east side.
for x in [1.69,2.36]:
 rod('Cot_long_rail',(x,1.42,.48),(x,3.58,.48),.023,steel)
 for y in [1.54,3.46]:
  rod('Cot_leg',(x,y,.04),(x,y,.48),.021,steel); box('Cot_foot',(x,y,.023),(.065,.075,.046),rubber)
for y in [1.44,3.56]: rod('Cot_end',(1.69,y,.48),(2.36,y,.48),.023,steel)
box('Cot_tension_canvas',(2.025,2.5,.504),(.635,2.04,.026),linen)
box('Cot_pad',(2.025,2.5,.558),(.66,2.03,.08),linen,.035)
box('Cot_pillow',(2.025,3.22,.645),(.57,.38,.115),paper,.05)
readyblanket=box('Arrival_blanket',(2.025,2.21,.619),(.665,1.20,.033),olive,.014)
for x in [1.724,2.326]: box('Blanket_woven_border',(x,2.21,.638),(.026,1.18,.004),linen,.001)
# Cupboard, west face against wall; front faces +X.
for x in [.41,.83]:
 for y in [.50,1.50]: box('Cupboard_foot',(x,y,.031),(.085,.085,.062),rubber)
for y in [.44,1.56]: box('Blanket_cupboard_side',(.62,y,.96),(.58,.04,1.8),pine)
box('Blanket_cupboard_back',(.345,1,.96),(.028,1.08,1.80),pine)
for z in [.08,.50,.94,1.38,1.84]: box('Blanket_shelf',(.635,1,z),(.55,1.08,.035),pine)
cup=mechanism('WSR_Blanket_cupboard_HINGE',(.929,.44,0),'Z',-105)
before=set(C.objects); box('Blanket_cupboard_door',(.929,1,.96),(.035,1.105,1.79),petrol)
box('Cupboard_inset_panel',(.951,1,1.10),(.014,.91,1.12),pine)
rod('Cupboard_handle',(.979,1.43,.86),(.979,1.43,1.05),.013,steel)
for o in set(C.objects)-before: parent(o,cup)
keyrot(cup,2,0,1); keyrot(cup,2,0,40); keyrot(cup,2,-105,80)
for z in [.59,1.03,1.47]:
 for y in [.72,1.25]:
  for j in range(3):
   box('Folded_wool_blanket',(.64,y,z+j*.062),(.45,.44,.054),olive,.021)
   box('Blanket_binding',(.869,y,z+j*.062),(.007,.40,.021),linen,.002)
# First-aid cabinet farther along west wall.
for y in [3.10,3.90]: box('Aid_cabinet_side',(.40,y,1.43),(.34,.035,.72),cream)
for z in [1.08,1.43,1.78]: box('Aid_cabinet_shelf',(.40,3.5,z),(.34,.77,.028),cream)
box('Aid_cabinet_back',(.216,3.5,1.43),(.026,.77,.69),cream)
aid=mechanism('WSR_First_aid_HINGE',(.59,3.10,1.07),'Z',-100)
before=set(C.objects); box('Aid_cabinet_door',(.59,3.5,1.43),(.034,.79,.7),cream)
box('Aid_symbol_square',(.611,3.5,1.47),(.008,.28,.28),green,.006)
box('Aid_symbol_vertical',(.617,3.5,1.47),(.005,.06,.20),paper,.001)
for y in [3.435,3.565]: box('Aid_symbol_arm',(.617,y,1.47),(.005,.07,.06),paper,.001)
for o in set(C.objects)-before: parent(o,aid)
keyrot(aid,2,0,1); keyrot(aid,2,0,40); keyrot(aid,2,-100,80)
for i in range(4): box('Aid_wrapped_packet',(.4,3.22+i*.18,1.21),(.22,.13,.22),paper)
for i in range(3): box('Aid_supply_box',(.4,3.25+i*.24,1.58),(.24,.19,.25),linen)
# Bag and splints on south equipment shelf. Hooks have visible mounting plates.
box('Equipment_shelf',(1.65,.37,1.04),(1.10,.43,.04),pine)
for x in [1.23,2.07]:
 rod('Shelf_bracket',(x,.14,.72),(x,.54,1.01),.014,steel); box('Shelf_mount',(x,.134,.87),(.045,.023,.34),steel)
box('First_aid_bag',(1.65,.36,1.240),(.56,.31,.36),orange,.06)
box('Bag_zipper',(1.65,.361,1.422),(.46,.02,.008),rubber,.002)
for x in [1.49,1.81]: rod('Bag_handle_upright',(x,.36,1.40),(x,.36,1.54),.012,rubber)
rod('Bag_handle',(1.49,.36,1.54),(1.81,.36,1.54),.012,rubber)
for i in range(3): box('Splint',(4.07+i*.07,.23,.80+i*.005),(.055,.05,1.24-i*.09),pine)
box('Splint_rack',(4.14,.26,.31),(.31,.21,.08),steel)
box('Rope_bag',(4.65,.43,.27),(.45,.38,.54),olive,.08)
for i in range(7):
 bpy.ops.mesh.primitive_torus_add(major_radius=.11+i*.002,minor_radius=.009,major_segments=24,minor_segments=8,location=(4.65,.43,.53+i*.012)); o=link(bpy.context.object); o.name='WSR_Rope_coil'; o.data.materials.append(linen)
for x in [4.10,4.40,4.70]:
 box('Hook_plate',(x,.127,1.66),(.07,.02,.10),steel)
 rod('Hook_stem',(x,.15,1.65),(x,.25,1.65),.012,steel); rod('Hook_return',(x,.25,1.65),(x,.25,1.70),.012,steel)
box('Boot_tray',(5.25,.52,.015),(.65,.54,.03),rubber)
for y in [.24,.80]: box('Boot_tray_rim',(5.25,y,.067),(.7,.022,.08),rubber)
for x in [4.91,5.59]: box('Boot_tray_rim',(x,.52,.067),(.022,.54,.08),rubber)
# Chair northwest, deliberately away from cot route.
for x in [.59,1.01]:
 for y in [4.09,4.51]: box('Chair_leg',(x,y,.23),(.043,.043,.44),pine)
box('Chair_seat',(.80,4.30,.47),(.5,.5,.055),pine,.025)
for x in [.59,1.01]: box('Chair_back_post',(x,4.52,.7),(.045,.045,.92),pine)
for z in [.78,.95]: box('Chair_back_slat',(.8,4.52,z),(.42,.035,.10),pine)
# Modest heater with real front grille spacing and separate dial.
box('Heater_housing',(3.55,4.58,.43),(.95,.22,.53),cream,.025)
box('Heater_dark_recess',(3.55,4.462,.43),(.80,.012,.37),rubber)
for i in range(17): box('Heater_grille',(3.18+i*.046,4.449,.43),(.016,.012,.35),cream,.003)
for x in [3.20,3.90]: box('Heater_bracket',(x,4.741,.39),(.045,.09,.25),steel)
dial=mechanism('WSR_Heater_thermostat_PIVOT',(4.14,4.74,1.15),'Y',250)
box('Thermostat_plate',(4.14,4.753,1.15),(.17,.055,.20),cream)
knob=rod('Thermostat_dial',(4.14,4.68,1.15),(4.14,4.72,1.15),.051,rubber); parent(knob,dial)
tick=box('Thermostat_pointer',(4.14,4.674,1.18),(.007,.004,.023),paper,.001); parent(tick,dial)
rod('Heater_conduit',(4.14,4.755,.36),(4.14,4.755,1.04),.01,steel)
rod('Heater_conduit_return',(3.99,4.755,.36),(4.14,4.755,.36),.01,steel)
label('Heater_label','REFUGE HEAT',(3.18,4.441,.68),.047,ink)
# Analog radio/checklist north wall, reachable and separate control pivots.
box('Radio_mount',(5.07,4.765,1.44),(.70,.04,.48),pine)
box('Radio_case',(5.08,4.61,1.47),(.58,.26,.32),petrol,.018)
box('Radio_scale',(4.98,4.474,1.51),(.29,.012,.09),paper,.002)
for i in range(8): box('Radio_scale_tick',(4.855+i*.032,4.465,1.51),(.003,.004,.05 if i%2 else .07),ink,.001)
for i in range(8): box('Radio_speaker_slot',(4.92+i*.02,4.471,1.405),(.007,.009,.08),rubber,.002)
for x in [5.20,5.30]:
 r=mechanism('WSR_Radio_dial_'+str(x),(x,4.46,1.5),'Y',270); o=rod('Radio_knob',(x,4.43,1.5),(x,4.48,1.5),.025,rubber); parent(o,r)
box('Radio_handset',(5.48,4.61,1.43),(.09,.09,.32),rubber,.035)
for i in range(18):
 t=i*.45; a=(5.48+.027*math.cos(t),4.58+.027*math.sin(t),1.25-i*.015); b=(5.48+.027*math.cos(t+.45),4.58+.027*math.sin(t+.45),1.235-i*.015); rod('Handset_coil',a,b,.006,rubber)
for i,(a,b) in enumerate([((5.48,4.58,1.285),(5.507,4.58,1.25)),((5.48+.027*math.cos(8.1),4.58+.027*math.sin(8.1),.98),(5.39,4.58,1.01)),((5.39,4.58,1.01),(5.34,4.58,1.32))]):rod('Handset_return_'+str(i),a,b,.006,rubber)
box('Readiness_board',(2.60,4.77,1.47),(.36,.025,.47),pine)
box('Readiness_paper',(2.60,4.753,1.47),(.30,.005,.40),paper,.001)
for x,z in [(2.60,1.47),(4.14,1.15),(5.07,1.44),(3.20,.39),(3.90,.39)]: box('North_wall_standoff',(x,4.789,z),(.065,.022,.09),steel)
label('Readiness_print','READY CHECK\n\n[ ] RADIO\n[ ] BLANKETS\n[ ] KIT\n[ ] HEAT',(2.465,4.748,1.61),.027)
rod('Pencil',(2.82,4.72,1.31),(2.82,4.72,1.52),.005,orange)
# Outside sign: original lettering, no protected logo.
box('Room_sign',(6.034,2.05,2.50),(.038,1.69,.25),cream,.01)
label('Room_sign_text','RESCUE / FIRST AID',(6.057,1.34,2.46),.116,ink,'west')
screws('Sign_screw',[(6.057,y,z) for y in [1.27,2.83] for z in [2.415,2.585]])
# Folding stretcher: two short textile sections, hinge blocks and locking sleeves.
st=empty('WSR_Stretcher_ROOT'); fold=mechanism('WSR_Stretcher_FOLD',(0,0,.075),'Y',180); parent(fold,st)
for half,sgn in [(0,-1),(1,1)]:
 before=set(C.objects)
 for y in [-.315,.315]:
  rod('Stretcher_rail',(sgn*.045,y,0),(sgn*1.075,y,0),.022,steel)
  rod('Stretcher_grip',(sgn*.88,y,0),(sgn*1.075,y,0),.028,rubber)
  box('Stretcher_hinge_cheek',(sgn*.028,y+sgn*.022,.035),(.045,.025,.11),steel,.004)
 for x in [sgn*.16,sgn*.76]:
  rod('Stretcher_crossbar',(x,-.315,-.04),(x,.315,-.04),.016,steel)
 # Closed thickness fabric with a shallow sag across width.
 verts=[]; nx,ny=10,8
 for layer in [0,1]:
  for i in range(nx+1):
   x=sgn*(.065+i*.79/nx)
   for j in range(ny+1):
    y=-.29+j*.58/ny; z=-.032*(1-(y/.29)**2)+layer*.008
    verts.append((x,y,z))
 faces=[]; N=(nx+1)*(ny+1)
 for i in range(nx):
  for j in range(ny):
   q=i*(ny+1)+j; f=(q,q+1,q+ny+2,q+ny+1); faces.extend([f,tuple(v+N for v in reversed(f))])
 boundary=[i*(ny+1) for i in range(nx+1)]+[nx*(ny+1)+j for j in range(1,ny+1)]+[i*(ny+1)+ny for i in range(nx-1,-1,-1)]+[j for j in range(ny-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]): faces.append((a,b,b+N,a+N))
 mesh=bpy.data.meshes.new('Tensioned_canvas'); mesh.from_pydata(verts,[],faces); mesh.update(); ob=bpy.data.objects.new('WSR_Stretcher_canvas',mesh); C.objects.link(ob); mesh.materials.append(orange)
 for x in [sgn*.25,sgn*.67]:
  box('Stretcher_restraint',(x,0,.024),(.042,.60,.012),rubber,.002); box('Stretcher_buckle',(x,.13,.037),(.065,.07,.013),steel,.003)
 for o in set(C.objects)-before: parent(o,fold if half else st)
 # Fold-under U legs: on the floor in the ready pose, tucked within each half for carrying/stow.
 leg=mechanism('WSR_Stretcher_LEG_'+str(half),(sgn*.67,0,-.065),'Y',sgn*90)
 parent(leg,fold if half else st)
 before=set(C.objects)
 for y in [-.265,.265]:
  rod('Stretcher_leg',(sgn*.67,y,-.065),(sgn*.67,y,-.730),.016,steel)
  box('Stretcher_leg_foot',(sgn*.67,y,-.738),(.063,.065,.024),rubber,.005)
 rod('Stretcher_leg_tie',(sgn*.67,-.265,-.63),(sgn*.67,.265,-.63),.014,steel)
 rod('Stretcher_leg_axle',(sgn*.67,-.34,-.065),(sgn*.67,.34,-.065),.012,steel)
 for o in set(C.objects)-before:parent(o,leg)
 for f,angle in [(1,sgn*90),(40,0),(80,0)]:keyrot(leg,1,angle,f)
for y in [-.315,.315]:
 o=rod('Stretcher_hinge_pin',(0,y-.04,.075),(0,y+.04,.075),.014,steel); parent(o,st)
 slide=empty('WSR_Stretcher_LOCK_SLIDE_'+str(y),(-.06,y,-.018)); parent(slide,st); slide['travel_axis']='X'; slide['release_travel_m']=-.16
 o=box('Stretcher_locking_sleeve',(-.06,y,-.018),(.15,.07,.075),petrol,.006); parent(o,slide)
 for f,xpos in [(1,-.22),(40,-.06),(80,-.06)]: slide.location.x=xpos; slide.keyframe_insert('location',frame=f)
for x in [3.07,3.22]:
 box('Stretcher_wall_plate',(x,.129,1.72),(.065,.025,.66),steel)
 for z in [1.17,2.20]:
  rod('Stretcher_bracket',(x,.15,z),(x,.55,z),.014,steel); rod('Stretcher_bracket_lip',(x,.55,z),(x,.55,z+.08),.014,steel)
for frame,pos,rot,ang in [(1,(3.07,.55,1.22),(0,90,0),180),(40,(3.80,2.25,.75),(0,0,90),0),(80,(3.80,2.25,.75),(0,0,90),0)]:
 st.location=pos; st.rotation_euler=tuple(math.radians(a) for a in rot); st.keyframe_insert('location',frame=frame); st.keyframe_insert('rotation_euler',frame=frame); keyrot(fold,1,ang,frame)
# Named gameplay anchors. Local +Y is approach/look direction, Z up.
for n,p,look in [('WSR_STRETCHER_STOW',(3.07,.55,1.22),(0,-1,0)),('WSR_STRETCHER_READY',(3.80,2.25,.75),(0,1,0)),('WSR_BLANKET_PLACE',(2.025,2.21,.65),(-1,0,0)),('WSR_HEATER_CONTROL',(4.14,4.67,1.15),(0,1,0)),('WSR_READINESS_CARD',(2.6,4.72,1.47),(0,1,0)),('WSR_RADIO_POINT',(5.08,4.43,1.47),(0,1,0))]:
 o=empty(n,p); o.rotation_euler=Vector(look).to_track_quat('Y','Z').to_euler(); o['control_height_m']=p[2]; o['approach_local_positive_Y']=list(look)
empty('WSR_ORIENTATION_EAST_PLUS_X',(6.2,0,0)); empty('WSR_ORIENTATION_NORTH_PLUS_Y',(0,1.4,0))
for name,f in [('NORMAL_EMPTY',1),('READY_FOR_ARRIVAL',40),('EQUIPMENT_OPEN',80)]: S.timeline_markers.new(name,frame=f)
S.frame_start=1; S.frame_end=80
# Set interpolation to constant: named poses, not claimed real-world folding animation.
for o in C.objects:
 if o.animation_data and o.animation_data.action:
  try:
   for layer in o.animation_data.action.layers:
    for strip in layer.strips:
     for slot in o.animation_data.action.slots:
      for fc in strip.channelbag(slot).fcurves:
       for k in fc.keyframe_points: k.interpolation='CONSTANT'
  except Exception: pass
S.frame_set(1)
# Usable individual UV layouts on all mesh objects; text stays editable.
for o in list(C.objects):
 if o.type=='MESH':
  bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
  bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False) if hasattr(bpy.ops.mesh,'normals_make_consistent') else None
  bpy.ops.uv.smart_project(island_margin=.025); bpy.ops.object.mode_set(mode='OBJECT')
  o['surface_owner']='WSR package: '+o.name
S.world=bpy.data.worlds.new('WSR_neutral_world'); S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.27,.30,1)
S.render.engine='CYCLES'; S.cycles.samples=24; S.cycles.use_denoising=True
S.render.resolution_x=1200; S.render.resolution_y=900; S.render.resolution_percentage=100
S.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Editable.blend'))
origin=[-37.45,0,4.60]
ref=json.loads((P/'reference_inspection.json').read_text())
manifest={'collection':'WSR_ASSETS','units':'metres','basis':'Z up; +Y gondola; +X east','authoring':'local; add origin once to root objects only','local_to_station_matrix':[[1,0,0,-37.45],[0,1,0,0],[0,0,1,4.6],[0,0,0,1]],'orientation_markers':{'WSR_ORIENTATION_EAST_PLUS_X':[6.2,0,0],'WSR_ORIENTATION_NORTH_PLUS_Y':[0,1.4,0]},'replace_collection':'WS_RESCUE_PROXY','delete_exactly':ref['collections']['WS_RESCUE_PROXY'],'shared_shell_patch':None,'surface_ownership':'Frames inset 4mm from aperture sides, narrow concealed packing; all frame visible reveals inside fixed rough openings. No shared shell faces changed. Threshold bottom at floor; sole top at +0.012m.','poses':{'NORMAL_EMPTY':1,'READY_FOR_ARRIVAL':40,'EQUIPMENT_OPEN':80},'export_only':'WSR_ASSETS mesh/font geometry; convert text on export copies; no empties except pivot/interaction metadata; no review context/cameras/lights','mechanisms':{},'objects':{}}
for o in C.objects:
 manifest['objects'][o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'rest_local_matrix':[list(row) for row in o.matrix_local],'dimensions_m':list(o.dimensions),'material_slots':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []}
 if 'axis' in o: manifest['mechanisms'][o.name]={'pivot_local':list(o.location),'axis':o['axis'],'closed':o['closed_degrees'],'open':o['open_degrees']}
(P/'assembly.json').write_text(json.dumps(manifest,indent=2))
print('ASSET BUILD COMPLETE',len(C.objects))



