"""Revision 03: continuous outward deck bands and front-projecting quarters."""
from pathlib import Path
base=Path(__file__).resolve().parents[2]/'visual_fidelity_02/scripts/build_redesign.py'
code=base.read_text()
code=code.replace("building('Quarters',.4,.7,6.1,4,3.35", "building('Quarters',.4,.7,6.1,5.7,3.35")
start=code.index('deck(-.2,7,5.39,7.2)')
end=code.index('# Straight rear staircase:',start)
code=code[:start]+'''
# Perimeter bands measured OUTWARD from the building envelope.
# 0.6m open inner grating, 2.4m solid promenade, 0.65m open outer grating.
def tiled(x0,x1,y0,y1,kind):
 nx=max(1,round((x1-x0)/1.2));ny=max(1,round((y1-y0)/1.2))
 for ix in range(nx):
  for iy in range(ny):
   a=x0+(x1-x0)*ix/nx+.004;b=x0+(x1-x0)*(ix+1)/nx-.004
   c=y0+(y1-y0)*iy/ny+.004;d=y0+(y1-y0)*(iy+1)/ny-.004
   (grating if kind=='grating' else solid)(a,b,c,d)
def ring(offset,width,kind):
 x0=-10.8-offset;x1=6+offset;y0=-3.5-offset;y1=5.4+offset
 tiled(x0-width,x1+width,y1,y1+width,kind)
 tiled(x0-width,x1+width,y0-width,y0,kind)
 tiled(x0-width,x0,y0,y1,kind)
 tiled(x1,x1+width,y0,y1,kind)
ring(0,.6,'grating');ring(.6,2.4,'solid');ring(3,.65,'grating')
# Rear access connects the building to its surrounding promenade.
tiled(-.7,6,-3.5,-.2,'solid')
tiled(5.94,6,-.2,5.4,'solid')
# Structural members stay beneath the walking surface.
for yy in [-7.15,-6.5,-4.1,-3.5,5.4,6,8.4,9.05]:
 box('Ring_long_girder',(-2.4,yy,-.20),(24.1,.11,.34),steel)
for xx in [-14.45,-13.8,-11.4,-10.8,6,6.6,9,9.65]:
 box('Ring_side_girder',(xx,.95,-.20),(.11,16.2,.34),steel)
for xx in [-13,-9,-5,-1,3,7,9.5]:
 for yy in [-6.7,8.65]:
  box('Promenade_support',(xx,yy,-.64),(.18,.18,.88),steel)
  box('Promenade_footing',(xx,yy,-1),(.45,.45,.14),concrete)
guard((-14.45,9.05,0),(3.8,9.05,0));guard((5.5,9.05,0),(9.65,9.05,0))
guard((9.65,-7.15,0),(9.65,9.05,0));guard((-14.45,-7.15,0),(-14.45,9.05,0))
guard((-14.45,-7.15,0),(9.65,-7.15,0))
''' +code[end:]
code=code.replace("group=decks;deck(-10.8,-.21,5.39,7.2);solid(-.8,0,1.35,2.75)","group=decks;solid(-.8,0,1.35,2.75)")
marker="group=stage\nfloor=material('Stage'"
fix='''
# Move the upper floor above a coherent transfer slab; no separate roof intersects it.
from mathutils import Matrix
for o in list(quarters.objects):o.location.z+=.3
bpy.context.view_layer.update()
for o in list(decks.objects):
 o.matrix_world=Matrix.Diagonal((1,1,3.65/3.35,1))@o.matrix_world
for o in list(assets.objects):
 if o.name.startswith(('Control_Roof','Roof_flashing','Roof_seam','Exposed_lower_roof_seam')):
  bpy.data.objects.remove(o,do_unlink=True)
group=assets
box('Interstorey_transfer_slab',(3.45,3.55,3.26),(6.3,5.9,.22),steel,.008)
box('Rear_roof_remainder',(2.9,.21,3.24),(6.16,.78,.18),steel,.008)
box('Left_roof_remainder',(.06,2.99,3.24),(.48,4.78,.18),steel,.008)
for yy in [.6,6.5]:box('Interstorey_fascia',(3.45,yy,3.40),(6.3,.045,.5),zinc,.004)
for xx in [.3,6.6]:box('Interstorey_fascia',(xx,3.55,3.40),(.045,5.9,.5),zinc,.004)
for xx in [.65,5.6]:
 beam('Front_cantilever_bracket',(xx,5.12,2.62),(xx,6.35,3.21),.11,steel)
 box('Bracket_mount',(xx,5.14,2.68),(.28,.06,.34),steel)
 for zz in [2.58,2.78]:bolt((xx,5.18,zz))
# Move radio furniture toward the new front windows; keep the rear entrance clear.
for o in quarters.objects:
 if o.name.startswith(('Radio_desk','Desk_leg','Radio_receiver','Frequency_display','Radio_tuning_knob','Microphone','Logbook','Writing_chair','Chair_leg')):o.location.y+=1.7
group=stage
floor=material('Stage' '''
code=code.replace(marker,fix.rstrip())
code=code.replace("(16,17,11),(2.5,2.3,2.7),48","(18,21,12),(2.5,3.3,2.7),44")
code=code.replace("(13,-13,9),(3,-.1,2.4),48","(16,-17,10),(3,-.1,2.4),44")
code=code.replace("(6.1,2.5,5.1),(2.3,3.0,4.1),23","(6.1,2.5,5.4),(2.3,3.8,4.4),23")
code=code.replace("family.data.ortho_scale=39","family.data.ortho_scale=46")
code=code.replace("'quarters_area_m2':6.1*4,'cantilever_m':.7","'quarters_area_m2':6.1*5.7,'front_cantilever_m':1.2,'side_cantilever_m':.7,'deck_bands_m':[.6,2.4,.65],'upper_floor_m':3.65")
code=code.replace("'riser_m':rise","'riser_m':3.65/20")
code=code.replace("(OUT/'design_manifest.json').write_text", "records[1]['footprint_m']=[6.1,5.7];records[1]['floor_z_m']=3.65\n(OUT/'design_manifest.json').write_text")
exec(compile(code,__file__,'exec'))
