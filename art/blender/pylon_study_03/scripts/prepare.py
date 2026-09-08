from pathlib import Path
p=Path('art/blender/pylon_study_03/scripts/build.py');s=Path('art/blender/pylon_study_02/scripts/build.py').read_text()
a=s.index('H=42.;shaft_top=43.55');b=s.index('# A central passenger lane')
legs='''H=42.;shaft_top=43.55
BASE_X=6.2;TOP_X=4.25;R0=.975;R1=.45
for side in [-1,1]:
 x0=side*BASE_X;x1=side*TOP_X
 box('Foundation_plinth',(x0,0,.4),(3.8,3.8,.8),concrete,.10)
 box('Raised_concrete_pedestal',(x0,0,1.0),(3.10,3.0,.4),concrete,.06)
 box('Base_plate',(x0,0,1.27),(2.75,2.7,.14),dark,.035)
 a=Vector((x0,0,1.34));b=Vector((x1,0,shaft_top));axis=(b-a).normalized()
 for k in range(4):
  t0=k/4;t1=(k+1)/4;q=a.lerp(b,t0);r=a.lerp(b,t1)
  tube('Tubular_leg_%s_section_%d'%(side,k+1),q,r,R0+(R1-R0)*t0,R0+(R1-R0)*t1)
  if k:flange('Leg_section_flange',q,R0+(R1-R0)*t0+.15,axis)
 flange('Foundation_anchor_flange',a+axis*.11,1.25,axis,24)
 # Anchored base with triangular fins: no pinched lower shaft.
 for k in range(8):
  angle=k*math.tau/8
  r0=.91;r1=1.21;z0=1.37;z1=2.20;th=.025
  coords=[(r0,-th,z0),(r1,-th,z0),(r0,-th,z1),(r0,th,z0),(r1,th,z0),(r0,th,z1)]
  vs=[(x0+x*math.cos(angle)-y*math.sin(angle),x*math.sin(angle)+y*math.cos(angle),z) for x,y,z in coords]
  me=bpy.data.meshes.new('Gusset');me.from_pydata(vs,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);o=bpy.data.objects.new('Anchor_gusset',me);parts.objects.link(o);me.materials.append(galv);bevel(o,.008)
 # Ladder tracks the tapered rear surface; it terminates at the transfer deck.
 def shaft(z):
  t=(z-a.z)/(b.z-a.z);return x0+(x1-x0)*t,R0+(R1-R0)*t
 for z in [1.6+i*.30 for i in range(137)]:
  x,rad=shaft(z);rod('Ladder_rung',(x-.23,rad+.22,z),(x+.23,rad+.22,z),.019)
 for dx in [-.26,.26]:
  xl,rl=shaft(1.55);xu,ru=shaft(43.35);rod('Ladder_stile',(xl+dx,rl+.24,1.55),(xu+dx,ru+.24,43.35),.026)
 xl,rl=shaft(1.55);xu,ru=shaft(42.55);rod('Fall_arrest_rail',(xl,rl+.27,1.55),(xu,ru+.27,42.55),.025,dark)
 x,r=shaft(2.48)
 box('Electrical_enclosure_frame',(x,-r-.018,2.48),(.66,.10,1.1),dark,.055)
 box('Electrical_enclosure_cover',(x,-r-.084,2.48),(.54,.035,.97),galv,.04)
 rod('Enclosure_handle',(x+.16,-r-.129,2.4),(x+.16,-r-.129,2.59),.018,dark)
 x,r=shaft(4.65);box('Tower_identity_plate',(x,-r-.025,4.65),(.76,.09,.98),dark,.03)
 text('Tower_number','03',(x,-r-.08,4.37),.50,white)
 x,r=shaft(5.35);text('Tower_id','MLD / LINE A',(x,-r-.07,5.35),.13,white)
 t0=(5.78-a.z)/(b.z-a.z);t1=(5.94-a.z)/(b.z-a.z)
 tube('Maintenance_band',a.lerp(b,t0),a.lerp(b,t1),R0+(R1-R0)*t0+.008,R0+(R1-R0)*t1+.008,amber)
'''
s=s[:a]+legs+s[b:]
s=s.replace('(7.7,1.45,1.0)','(10.5,1.60,1.0)').replace('(7.9,1.60,.08)','(10.7,1.75,.08)')
s=s.replace('(side*3.3,0,40.1),(side*1.95,0,43.55),.23,.20','(side*4.42,0,39.8),(side*2.55,0,43.55),.26,.22')
s=s.replace('side*3.35','side*4.72').replace('side*2.45','side*3.55')
s=s.replace("for y in [-2.1,2.1]:\n box('Central_suspension_drop',(-.58,y,42.58),(.20,.24,2.14),dark,.035)","box('Central_suspension_drop',(-.62,0,42.55),(.32,.58,2.22),dark,.035)")
s=s.replace("rod('Main_rocker_pin',(-.75,0,41.45),(-.32,0,41.45),.16,dark)","rod('Main_rocker_pin',(-.86,0,41.45),(-.32,0,41.45),.16,dark)\nfor xx in [-.84,-.34]:tube('Main_pin_retaining_cap',(xx-.025,0,41.45),(xx+.025,0,41.45),.185,mat=galv,verts=32)")
s=s.replace("for center in [-2.1,2.1]:\n box('Secondary_rocker'", "for center in [-2.1,2.1]:\n box('Secondary_pivot_link',(-.34,center,41.65),(.13,.32,.34),dark,.025)\n rod('Secondary_equalizer_pin',(-.47,center,41.78),(-.19,center,41.78),.09,galv)\n box('Secondary_rocker'")
s=s.replace("for y in [-2.9,2.9]:\n tube('Deck_hanger',(-1.5,y,42.40),(-1.5,y,43.52),.055,mat=dark)","for y in [-2.1,2.1]:\n tube('Deck_hanger',(-1.5,y,42.40),(-1.5,y,43.52),.065,mat=dark)\n box('Deck_support_outrigger',(-1.04,y,43.55),(1.12,.20,.20),dark,.025)")
s=s.replace("for x in [-3.1+i*.13 for i in range(10)]:box('Ladder_transfer_grating',(x,1.18,42.55),(.04,.72,.065),galv,.004)","for x in [-4.32+i*.13 for i in range(23)]:box('Ladder_transfer_grating',(x,1.18,42.55),(.04,.72,.065),galv,.004)\nbox('Transfer_deck_stringer',(-2.93,1.18,42.43),(2.96,.16,.18),dark,.02)\ntube('Transfer_bracket',(-4.4,.10,41.6),(-4.28,1.18,42.43),.085,mat=dark)")
# Give return rope the same running sheave diameter as the main rope.
s=s.replace('44.90','44.975').replace('),.20,mat=rubber,verts=32)', '),.275,mat=rubber,verts=32)').replace('),.22,mat=galv,verts=32)', '),.293,mat=galv,verts=32)').replace('45.132','45.282')
# Illustrative shallow-sag rope geometry: curved support bank, then a parabolic span.
needle='# One central 12-sheave support assembly.'
func='''ROPE_H=250000.;ROPE_W=12.*9.81;SPAN=300.;EDGE=3.7
EDGE_SLOPE=ROPE_W*SPAN/(2*ROPE_H);CURVE_A=EDGE_SLOPE/(2*EDGE)
def rope_z(y):
 u=abs(y)
 if u<=EDGE:return 42.327-CURVE_A*u*u
 d=u-EDGE;return 42.327-CURVE_A*EDGE*EDGE-ROPE_W*d*(SPAN-d)/(2*ROPE_H)
def rope_slope(y):
 sign=1 if y>=0 else -1;u=abs(y)
 return -sign*(2*CURVE_A*u if u<=EDGE else ROPE_W*(SPAN-2*(u-EDGE))/(2*ROPE_H))
'''
s=s.replace(needle,func+needle)
s=s.replace('y=center+offset;z=42.02',"yp=center+offset;normal=Vector((0,-rope_slope(yp),1)).normalized();contact=Vector((0,yp,rope_z(yp)));wheel=contact-normal*(.275+.032);y=wheel.y;z=wheel.z")
s=s.replace("rod('STUDY_central_passenger_rope',(0,-32,42.327),(0,32,42.327),.032,dark)","for i in range(256):\n y=-32+i*.25;y2=y+.25\n rod('STUDY_central_passenger_rope',(0,y,rope_z(y)),(0,y2,rope_z(y2)),.032,dark)")
s=s.replace("rod('STUDY_bare_return_rope',(-2.35,-32,45.282),(-2.35,32,45.282),.032,dark)","for i in range(128):\n y=-32+i*.5;y2=y+.5\n def return_z(q):return 45.282 if abs(q)<1 else 45.282-ROPE_W*(abs(q)-1)*(SPAN-(abs(q)-1))/(2*ROPE_H)\n rod('STUDY_bare_return_rope',(-2.35,y,return_z(y)),(-2.35,y2,return_z(y2)),.032,dark)")
# Move cabin with the sag at its initial position; preserve upright gravity orientation.
s=s.replace('cabin_objects+=adapter',"cabin_objects+=adapter\nfor ob in cabin_objects:ob.location.z+=rope_z(-7)-42.327")
s=s.replace('ob.location.y+=7', 'ob.location.y+=7;ob.location.z+=rope_z(0)-rope_z(-7)').replace('ob.location.y-=7', 'ob.location.y-=7;ob.location.z-=rope_z(0)-rope_z(-7)')
s=s.replace('Maldek_Weathered_Central_Pylon','Maldek_Tapered_Central_Pylon').replace('SM_Maldek_Central_Pylon','SM_Maldek_Tapered_Pylon')
s=s.replace("'design_height_m':45.12", "'design_height_m':45.268").replace("'base_leg_spacing_m':9.2", "'base_leg_spacing_m':12.4,'top_leg_spacing_m':8.5").replace("'shaft_diameter_base_m':2.1", "'shaft_diameter_base_m':1.95").replace("'shaft_diameter_top_m':1.42", "'shaft_diameter_top_m':.90")
s=s.replace("(15,-23,46),(0,0,42),57", "(18,-27,47),(0,0,42),57").replace("(0,-29,40.8),(0,0,40.8),55", "(0,-34,40.8),(0,0,40.8),55")
s=s.replace("'Maldek single central passenger lane / overhead portal / weathered finish'", "'Maldek wider tapered portal / pinned central equalizer / explicit load path'")
p.write_text(s)
