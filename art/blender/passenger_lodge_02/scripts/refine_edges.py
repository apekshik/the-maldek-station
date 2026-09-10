"""Executed by build.py before route checks; alter combined scene only."""
# Narrow the west promenade, keeping rails and supporting columns aligned.
for ob in list(c.objects):
 lo,hi=bounds(ob)
 if ob.name.startswith('PL02_Deck') and lo[0]<-31:
  ob.dimensions.x-=2;ob.location.x+=1
 elif ob.name.startswith('PL02_Perimeter'):
  # Transform endpoints in mesh world coordinates so cross rails shorten too.
  ob.data=ob.data.copy()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co
   if p.x<-31:p.x+=2
   v.co=ob.matrix_world.inverted()@p
 elif ob.name.startswith('PL02_Support') and ob.location.x<-30:ob.location.x+=2

# Remove the obsolete isolated deck tab; relocate the real arrival assembly.
tab=bpy.data.objects.get('PL02_Deck_021')
if tab:bpy.data.objects.remove(tab,do_unlink=True)
bpy.context.view_layer.update()
moving=[]
for ob in list(s.objects):
 if ob.type!='MESH' or not ob.visible_get():continue
 lo,hi=bounds(ob)
 if lo[0]>-24 and hi[0]<-12 and hi[1]<-15.14 and lo[2]>-.4:
  moving.append(ob)
# Source objects belong to shared collections: substitute copies in this scene.
source_moving=[o for o in moving if o.name not in c.objects]
affected_arrival={cc for o in source_moving for cc in o.users_collection}
for cc in affected_arrival:
 for ob in list(cc.objects):
  if ob in source_moving:
   dup=ob.copy();dup.data=ob.data;dup.name='PL02_Shifted_'+ob.name
   ret.objects.link(dup);world=ob.matrix_world.copy();dup.parent=None;dup.matrix_world=world;dup.location.x-=1.5
  elif ob.name not in ret.objects:ret.objects.link(ob)
exclude(s.view_layers[0].layer_collection,{cc.name for cc in affected_arrival})
for ob in moving:
 if ob.name in c.objects:ob.location.x-=1.5
# Rebuild the rear guard to match the shifted arrival opening.
for ob in list(c.objects):
 if ob.name.startswith(('PL02_Perimeter_2','PL02_Perimeter_3')):bpy.data.objects.remove(ob,do_unlink=True)
rail('PL02_Rear_West',(-29.45,-15.15),(-24.5,-15.15))
rail('PL02_Rear_East',(-22.5,-15.15),(-8.1,-15.15))

# A stairwell must cut every deck slab, including the retained east footprint.
well=(-8.1,-6.3,-15.15,-7.7)
landing=(-10.1,-6.3,-7.7,-5.7)
for ob in list(c.objects):
 if not ob.name.startswith('PL02_Deck'):continue
 lo,hi=bounds(ob);rect=(lo[0],hi[0],lo[1],hi[1]);parts=[rect]
 for h in (well,landing):parts=[p for q in parts for p in subtract(q,h)]
 if parts==[rect]:continue
 name=ob.name;bpy.data.objects.remove(ob,do_unlink=True)
 for j,(x0,x1,y0,y1) in enumerate(parts):box(name+'_Cut_'+str(j),x0,y0,3.8,x1-x0,y1-y0,.2,plate)
# Protect the exposed outer edge of the well; the inner stair rail supplies its side.
rail('PL02_Well_Guard',(-6.3,-13.2),(-6.3,-7.7))
for route in layout['routes']:
 if route['name']=='Arrival turn onto platform':
  route['points']=[[p[0]-1.5,p[1],p[2]] for p in route['points']]
print('Refined platform edges and stair opening; arrival moved 1.5 m west',flush=True)
