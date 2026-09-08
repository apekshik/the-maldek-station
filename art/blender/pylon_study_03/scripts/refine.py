from pathlib import Path
p=Path('art/blender/pylon_study_03/scripts/build.py');s=p.read_text()
s=s.replace(" box('Foundation_plinth',(x0,0,.4),(3.8,3.8,.8),concrete,.10)"," tube('Buried_foundation_socket',(x0,0,-6),(x0,0,0),1.60,mat=concrete,verts=48)\n box('Foundation_plinth',(x0,0,.4),(3.8,3.8,.8),concrete,.10)\n for xx in [-1.48,1.48]:\n  for yy in [-1.48,1.48]:\n   box('Foundation_anchor_head',(x0+xx,yy,.86),(.28,.28,.12),dark,.015)\n   tube('Foundation_anchor_stud',(x0+xx,yy,.82),(x0+xx,yy,1.04),.045,mat=galv,verts=12)")
a=s.index('for i in range(256):');b=s.index("figure=material('STUDY_Scale_Figure'",a)
s=s[:a]+'''def study_rope(name,points):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=.032;c.bevel_resolution=3;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);stage.objects.link(o);c.materials.append(dark)
study_rope('STUDY_central_passenger_rope',[(0,-32+i*.25,rope_z(-32+i*.25)) for i in range(257)])
def return_z(q):return 45.282 if abs(q)<1 else 45.282-ROPE_W*(abs(q)-1)*(SPAN-(abs(q)-1))/(2*ROPE_H)
study_rope('STUDY_bare_return_rope',[(-2.35,-32+i*.25,return_z(-32+i*.25)) for i in range(257)])
'''+s[b:]
s=s.replace(" adapter.append(tube('STUDY_CABIN_hanger_adapter',a,b,.060,mat=dark,verts=16))", " d=Vector(b)-Vector(a);o=box('STUDY_CABIN_hanger_adapter',(Vector(a)+Vector(b))/2,(.14,.20,d.length),dark,.025);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();adapter.append(o)")
s=s.replace("'base_leg_spacing_m':12.4", "'buried_socket_depth_m':6.,'base_leg_spacing_m':12.4")
p.write_text(s)
p=Path('art/blender/pylon_study_03/scripts/physics_review.py');s=p.read_text()
s=s.replace("F=top_total/2;Mbase=F*mast_h+sum(q*z*dz for z,D,A,I,q in rows)","F=top_total/2;top_vertical=head_mass*g/2+reaction_total/2\n gravity_eccentric_moment=top_vertical*1.95+sum(A*rho*g*dz*1.95*z/mast_h for z,D,A,I,q in rows)\n Mbase=F*mast_h+sum(q*z*dz for z,D,A,I,q in rows)+gravity_eccentric_moment")
s=s.replace("M=F*(mast_h-z)+sum(q2*(z2-z)*dz for z2,D2,A2,I2,q2 in rows[j:])", "M=F*(mast_h-z)+sum(q2*(z2-z)*dz for z2,D2,A2,I2,q2 in rows[j:])\n  M+=top_vertical*1.95*(mast_h-z)/mast_h+sum(A2*rho*g*dz*1.95*(z2-z)/mast_h for z2,D2,A2,I2,q2 in rows[j:])")
s=s.replace("'base_moment_per_leg_kNm':Mbase/1000", "'conservative_gravity_eccentric_moment_kNm':gravity_eccentric_moment/1000,'base_moment_per_leg_kNm':Mbase/1000")
p.write_text(s)
