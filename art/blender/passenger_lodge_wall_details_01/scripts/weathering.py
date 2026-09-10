"""Localized age: edge chips, ledge dust, prior pin puncture marks. Run inside build.py."""
import random
rng=random.Random(199109)
dust=material('Settled_dust',(.30,.27,.20),0,.98);exposed=material('Frame_edge_scuffs',(.40,.27,.115),0,.88);oldpin=material('Old_pin_marks',(.075,.039,.016),0,1)
for parent in list(roots):
 if any(parent.name.startswith('PLG_'+n) for n in ['Poster_','Timetable','Visitor_map']):
  w,h=parent['display_size_m'];front=.060 if parent.name in ['PLG_Timetable','PLG_Visitor_map'] else .037
  # Narrow discontinuous settled dust on upward-facing ledge, each strip 0.3 mm thick.
  for i in range(4):
   x=(-.34+i*.21)*w;box(parent.name+'_ledge_dust',parent,(x,h/2+.00018,front*.55),(w*.15,.0003,front*.34),dust,.0001)
  for i in range(7):
   side=-1 if i%2 else 1;x=side*(w/2-.011);y=rng.uniform(-h*.42,h*.42)
   o=box(parent.name+'_edge_scuff',parent,(x,y,front+.00025),(.0015,rng.uniform(.005,.017),.0004),exposed,0);o.rotation_euler.z=rng.uniform(-.18,.18)
# Retired pin positions scattered mostly on the unused community-board half.
board=bpy.data.objects['PLG_Community']
for i in range(19):
 x=rng.uniform(.27,.69);y=rng.uniform(-.42,.31);cyl('Old_pin_puncture_mark',board,(x,y,.03435),rng.uniform(.00055,.0011),.0004,oldpin)
# A few darker fasteners retain metal appearance; no blanket rust field.
for o in col.objects:
 if o.type=='MESH' and '_fixing' in o.name and o.name.endswith('.001'):o.data.materials[0]=steel
