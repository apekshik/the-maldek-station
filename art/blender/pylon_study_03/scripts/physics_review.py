"""Illustrative statics only: assumptions are not the actual ropeway specification."""
import math,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]
g=9.81;L=300.;mu=12.;H=250000.;m=1800.;dyn=1.5
w=mu*g;P=m*g;loaded=P*dyn
sag_empty=w*L*L/(8*H);sag_loaded=sag_empty+P*L/(4*H)
reaction_per_bare_run=w*L;reaction_total=2*reaction_per_bare_run+loaded
mast_h=42.21;rho=7850.;E=210e9;n=1000;dz=mast_h/n
qwind=.5*1.225*30**2;cd=1.2
rows=[]
for i in range(n):
 z=(i+.5)*dz;t=z/mast_h;D=1.95-1.05*t;wall=.025-.009*t;di=D-2*wall
 A=math.pi/4*(D*D-di*di);I=math.pi/64*(D**4-di**4)
 rows.append((z,D,A,I,qwind*cd*D))
leg_mass=sum(A*rho*dz for z,D,A,I,q in rows)
head_mass=12000.;head_wind=qwind*1.6*10.5
# Two distinct horizontal cases: wind transverse; a hypothetical 20% tension imbalance longitudinal.
cases=[]
for label,top_total in [('wind_only',head_wind+8000),('wind_plus_assumed_20pct_rope_imbalance',head_wind+8000+.2*H)]:
 F=top_total/2;top_vertical=head_mass*g/2+reaction_total/2
 gravity_eccentric_moment=top_vertical*1.95+sum(A*rho*g*dz*1.95*z/mast_h for z,D,A,I,q in rows)
 Mbase=F*mast_h+sum(q*z*dz for z,D,A,I,q in rows)+gravity_eccentric_moment
 axial=(2*leg_mass+head_mass)*g/2+reaction_total/2
 A0=math.pi/4*(1.95**2-1.90**2);I0=math.pi/64*(1.95**4-1.90**4);sigma=axial/A0+Mbase*(1.95/2)/I0
 # First-order cantilever integration. Omits frame action, local buckling, joint flexibility and P-delta.
 deflect=0.
 for j,(z,D,A,I,q) in enumerate(rows):
  M=F*(mast_h-z)+sum(q2*(z2-z)*dz for z2,D2,A2,I2,q2 in rows[j:])
  M+=top_vertical*1.95*(mast_h-z)/mast_h+sum(A2*rho*g*dz*1.95*(z2-z)/mast_h for z2,D2,A2,I2,q2 in rows[j:])
  deflect+=M*(mast_h-z)/(E*I)*dz
 cases.append({'case':label,'conservative_gravity_eccentric_moment_kNm':gravity_eccentric_moment/1000,'base_moment_per_leg_kNm':Mbase/1000,'gross_elastic_base_stress_MPa':sigma/1e6,'first_order_tip_deflection_m':deflect,'axial_load_per_leg_kN':axial/1000,'shallow_pad_eccentricity_m':Mbase/axial,'shallow_pad_middle_third_limit_m':3.8/6})
report={'purpose':'Order-of-magnitude plausibility review; no capacity approval or real-world certification','assumptions':{'level_span_m':L,'rope_mass_kg_per_m':mu,'horizontal_rope_tension_per_run_kN':H/1000,'loaded_cabin_mass_kg':m,'illustrative_dynamic_multiplier':dyn,'wind_speed_m_s':30,'steel_E_GPa':210,'steel_density_kg_m3':rho,'shaft_wall_base_mm':25,'shaft_wall_top_mm':16,'head_mass_kg':head_mass},'results':{'empty_midspan_sag_m':sag_empty,'midspan_sag_with_stationary_cabin_m':sag_loaded,'vertical_rope_and_dynamic_cabin_reaction_kN':reaction_total/1000,'steel_mass_per_leg_kg':leg_mass,'cases':cases},'design_actions':['Keep a full base section; taper from 1.95 m diameter to 0.90 m at the crown.','Use pinned primary and secondary sheave equalizers connected to an overhead girder.','Represent concrete plinths as caps on buried foundations; shallow pads alone fail the illustrative eccentricity screen.','Provide an actual grip and articulated hanger load path; rendered clearance is not a grip strength test.','At route integration use surveyed span elevations, specified rope properties, carrier mass, wind limits and competent structural design.'],'not_checked':['Rope breaking strength and fatigue','Grip clamping/slip capacity','Shaft local/global buckling and fatigue','Bolted/welded connection capacities','Rock-anchor, soil and foundation capacities','Emergency braking, ice, seismic, real wind and operating limits','Geometric nonlinear response and full frame dynamics'],'sources':['https://www.leitner.com/fileadmin/userdaten/00-home/Ordner-Facelift/PDF_s_Logo_neu/Strecke/The_LEITNER_Line_.pdf','https://ceae.colorado.edu/~saouma/files/Saouma-Structural-Analysis-Lecture-Notes.pdf']}
(out/'physics_review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
