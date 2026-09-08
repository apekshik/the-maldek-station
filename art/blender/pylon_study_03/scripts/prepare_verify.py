from pathlib import Path
s=Path('art/blender/pylon_study_02/scripts/verify_clearance.py').read_text().replace('Maldek_Weathered_Central_Pylon','Maldek_Tapered_Central_Pylon').replace('from mathutils import Vector','from mathutils import Vector,Matrix')
a=s.index('collisions=[]');b=s.index("report={'passenger_lanes'",a)
s=s[:a]+'''collisions=[]
travel=[-6+i*.25 for i in range(49)]
angles=[-8,0,8]
w=12*9.81;H=250000.;span=300.;edge=3.7;ca=(w*span/(2*H))/(2*edge)
def rope_z(y):
 u=abs(y)
 if u<=edge:return 42.327-ca*u*u
 d=u-edge;return 42.327-ca*edge*edge-w*d*(span-d)/(2*H)
cache={o:meshdata(o) for o in cabin}
for position in travel:
 dy=position+7;dz=rope_z(position)-rope_z(-7)
 pivot=Vector((.1,position,41.36+rope_z(position)-42.327))
 for angle in angles:
  rot=Matrix.Rotation(math.radians(angle),3,'Y')
  for o in cabin:
   vs,fs=cache[o]
   if not fs:continue
   shifted=[v+Vector((0,dy,dz)) for v in vs]
   if 'hanger_adapter' not in o.name:shifted=[pivot+rot@(v-pivot) for v in shifted]
   ct=BVHTree.FromPolygons(shifted,fs,all_triangles=True)
   overlap=pt.overlap(ct)
   if overlap:collisions.append({'cabin':o.name,'travel_y':position,'swing_deg':angle,'pylon_parts':sorted(set(owners[a] for a,b in overlap)),'triangle_pairs':len(overlap)})
'''+s[b:]
s=s.replace("'tested_cabin_travel_positions_m':travel", "'tested_cabin_travel_positions_m':travel,'illustrative_body_swing_degrees':angles,'poses_checked':len(travel)*len(angles)")
Path('art/blender/pylon_study_03/scripts/verify_clearance.py').write_text(s)
