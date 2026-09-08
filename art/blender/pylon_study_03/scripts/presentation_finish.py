from pathlib import Path
p=Path('art/blender/pylon_study_03/scripts/build.py');s=p.read_text()
s=s.replace('range(137)','range(137 if side<0 else 0)').replace('for dx in [-.26,.26]:','for dx in ([-.26,.26] if side<0 else []):')
s=s.replace("xl,rl=shaft(1.55);xu,ru=shaft(42.55);rod('Fall_arrest_rail'", "xl,rl=shaft(1.55);xu,ru=shaft(42.55)\n if side<0:rod('Fall_arrest_rail'")
s=s.replace("for y in [-3.65,3.65]:\n box('Central_rope_sensor'", "for y in [-3.65,3.65]:\n rod('Sensor_support_stalk',(-.30,y,41.9),(-.30,y,42.35),.025,dark)\n box('Central_rope_sensor'")
s=s.replace(" if name=='04_front_clearance':\n  for ob in cabin_objects:ob.location.y+=7", " if name=='04_front_clearance':\n  for ob in stage.objects:\n   if ob.name.startswith(('STUDY_central_passenger_rope','STUDY_bare_return_rope')):ob.hide_render=True\n  for ob in cabin_objects:ob.location.y+=7")
s=s.replace(" if name=='04_front_clearance':\n  for ob in cabin_objects:ob.location.y-=7", " if name=='04_front_clearance':\n  for ob in stage.objects:\n   if ob.name.startswith(('STUDY_central_passenger_rope','STUDY_bare_return_rope')):ob.hide_render=False\n  for ob in cabin_objects:ob.location.y-=7")
p.write_text(s)
