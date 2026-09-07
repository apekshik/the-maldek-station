"""Triple both grating bands and increase the solid promenade width by 50%."""
from pathlib import Path
previous=Path(__file__).resolve().parents[2]/'visual_fidelity_04/scripts/build_detail_pass.py'
exec(compile(previous.read_text().rsplit("exec(compile(code,__file__,'exec'))",1)[0],__file__,'exec'))
code=code.replace("ring(0,.6,'grating');ring(.6,2.4,'solid');ring(3,.65,'grating')", "ring(0,1.8,'grating');ring(1.8,3.6,'solid');ring(5.4,1.95,'grating')")
code=code.replace("[-7.15,-6.5,-4.1,-3.5,5.4,6,8.4,9.05]", "[-10.85,-8.9,-5.3,-3.5,5.4,7.2,10.8,12.75]")
code=code.replace("(24.1,.11,.34)","(31.5,.11,.34)").replace("(.11,16.2,.34)","(.11,23.6,.34)")
code=code.replace("[-14.45,-13.8,-11.4,-10.8,6,6.6,9,9.65]", "[-18.15,-16.2,-12.6,-10.8,6,7.8,11.4,13.35]")
code=code.replace("[-13,-9,-5,-1,3,7,9.5]", "[-17,-13,-9,-5,-1,3,7,11,13]").replace("[-6.7,8.65]","[-9.9,11.8]")
# Outer main guard locations only, not the earlier building dimensions.
for old,new in [('(-14.45','(-18.15'),('(9.65','(13.35'),(',9.05,0)',',12.75,0)'),(',-7.15,0)',',-10.85,0)')]:code=code.replace(old,new)
# Preserve utility asset coordinates during creation; move their collections together below.
# All three bands also expand on the service-building aprons.
code=code.replace("tiled(x0,x1,y,y+.6,'grating');tiled(x0,x1,y+.6,y+3,'solid');tiled(x0,x1,y+3,y+3.65,'grating')", "tiled(x0,x1,y,y+1.8,'grating');tiled(x0,x1,y+1.8,y+5.4,'solid');tiled(x0,x1,y+5.4,y+7.35,'grating')")
code=code.replace("[y,y+.6,y+3,y+3.65]", "[y,y+1.8,y+5.4,y+7.35]").replace("[y+.25,y+3.4]","[y+.3,y+7.05]")
# Rebuild connecting bridges after the asset relocation; discard their old short versions.
code=code.replace("tiled(13.35,10.8,.1,2.2,'solid')", "")
code=code.replace("tiled(13.35,10.8,6.1,10.7,'solid')", "")
code=code.replace("guard((10.8,2.85,0),(20.2,2.85,0));guard((20.2,-2.3,0),(20.2,2.85,0))", "guard((10.8,6.55,0),(20.2,6.55,0));guard((20.2,-2.3,0),(20.2,6.55,0))")
code=code.replace("guard((10.8,11.85,0),(15.2,11.85,0))", "guard((10.8,15.55,0),(15.2,15.55,0))")
extra=r'''
# Clear the widened main ring by moving each utility assembly eight metres east.
move_cols=[service,relay,utilitydeck,tankcol,props]
bpy.context.view_layer.update()
for c in move_cols:
 for o in c.objects:
  points=[o.matrix_world@Vector(v) for v in o.bound_box];cx=sum(p.x for p in points)/8;cy=sum(p.y for p in points)/8
  if c==props and cx<10:continue
  o.location.x+=8
  if c in [relay,tankcol] or (c in [utilitydeck,props] and cy>7):o.location.y+=5
for o in details.objects:
 if o.location.x>10:
  o.location.x+=8
  if o.location.y>7:o.location.y+=5
bpy.data.objects['Tank_daylight'].location.x+=8
bpy.data.objects['Tank_daylight'].location.y+=5
group=utilitydeck
tiled(13.35,18.8,.3,3.9,'solid')
tiled(13.35,18.8,9.05,17.65,'solid')
for y in [.3,3.9,9.05,17.65]:
 box('Wide_link_girder',(16.075,y,-.2),(5.45,.14,.34),steel)
 guard((13.35,y,0),(18.8,y,0))
for x in [14,18.2]:
 for y in [.6,3.6,9.35,13.35,17.35]:box('Wide_link_pier',(x,y,-.66),(.38,.38,.95),concrete)
guard((13.35,12.75,0),(13.35,17.65,0))
'''
idx=code.rfind("group=stage\nfloor=material('Stage'");code=code[:idx]+extra+code[idx:]
# Main side railing has 3.6m wide entrances matching the new connecting decks.
code=code.replace("guard((13.35,-10.85,0),(13.35,.1,0));guard((13.35,2.2,0),(13.35,6.1,0));guard((13.35,8,0),(13.35,12.75,0))", "guard((13.35,-10.85,0),(13.35,.3,0));guard((13.35,3.9,0),(13.35,9.05,0));guard((13.35,12.65,0),(13.35,12.75,0))")
code=code.replace("(18,21,12),(2.5,3.3,2.7),44", "(23,28,16),(2.5,3.5,2.4),43")
code=code.replace("(28,25,12),(18,13.3,3.5),42", "(36,30,12),(26,18.3,3.5),42")
code=code.replace("(21,7,4),(15,-.1,1.4),40", "(29,9,5),(23,.5,1.4),40")
code=code.replace("family.data.ortho_scale=52", "family.data.ortho_scale=65")
code=code.replace("(34,38,29),(4,-1,1.6),40", "(42,43,32),(7,4,1.6),40")
code=code.replace("'deck_bands_m':[.6,2.4,.65]", "'deck_bands_m':[1.8,3.6,1.95],'utility_shift_east_m':8")
exec(compile(code,__file__,'exec'))
