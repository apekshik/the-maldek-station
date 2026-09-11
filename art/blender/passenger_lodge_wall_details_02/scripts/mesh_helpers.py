def material(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new('PLG2_'+n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def tex(name):
 if name in textures:return textures[name]
 m=material('Ink_'+name,(.8,.8,.8),0,.74);n=m.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(P/'textures'/f'{name}.png'),check_existing=True);im.pack();im.filepath='//textures/'+name+'.png';n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);textures[name]=m;return m

def root(name,pos,u):
 o=bpy.data.objects.new('PLG2_'+name,None);col.objects.link(o);u=Vector(u);v=Vector((0,0,1));n=u.cross(v);o.matrix_world=Matrix(((u.x,v.x,n.x,pos[0]),(u.y,v.y,n.y,pos[1]),(u.z,v.z,n.z,pos[2]),(0,0,0,1)));o['assembly_origin']='Back centre at mount plane; local X right, Y up, Z face normal';roots.append(o);return o

def box(name,parent,loc,dims,mat,bevel=0):
 vs=[(x*dims[0]/2,y*dims[1]/2,z*dims[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();o=bpy.data.objects.new('PLG2_'+name,me);col.objects.link(o);o.parent=parent;o.location=loc
 uv=me.uv_layers.new(name='Surface_UV')
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x+0.5,v.y+0.5)
 o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Machined edge','BEVEL');mod.width=bevel;mod.segments=3
 return o

def face(name,parent,w,h,z,art,thick=.00035,curl=0):
 # Thin closed paper slab, grid front/back supports actual controlled corner curl.
 nx=16 if curl else 1;ny=16 if curl else 1;vs=[]
 for back in [0,1]:
  for j in range(ny+1):
   for i in range(nx+1):
    x=i/nx;y=j/ny;delta=curl*max(0,(x-.65)/.35)**2*max(0,(.35-y)/.35)**2;vs.append(((x-.5)*w,(y-.5)*h,z+delta-back*thick))
 stride=nx+1;N=(nx+1)*(ny+1);fs=[];front=[]
 for j in range(ny):
  for i in range(nx):
   a=j*stride+i;fs.extend([(a,a+1,a+1+stride,a+stride),(N+a+stride,N+a+1+stride,N+a+1,N+a)]);front.extend([True,False])
 perimeter=list(range(nx+1))+[j*stride+nx for j in range(1,ny+1)]+[ny*stride+i for i in range(nx-1,-1,-1)]+[j*stride for j in range(ny-1,0,-1)]
 for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):fs.append((a,N+a,N+b,b));front.append(False)
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('PLG2_'+name,me);col.objects.link(o);o.parent=parent;me.materials.append(paper);me.materials.append(tex(art));uv=me.uv_layers.new(name='Artwork_0_1')
 for p,yes in zip(me.polygons,front):
  p.material_index=int(yes)
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x/w+.5,co.y/h+.5)
 o['artwork']=art;o['paper_thickness_m']=thick;o['max_corner_curl_m']=curl;return o

def cyl(name,parent,loc,r,depth,mat,axis='Z'):
 vs=[(r*math.cos(i*math.tau/32),r*math.sin(i*math.tau/32),z*depth/2) for z in [-1,1] for i in range(32)];fs=[tuple(range(31,-1,-1)),tuple(range(32,64))]+[(i,(i+1)%32,(i+1)%32+32,i+32) for i in range(32)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('PLG2_'+name,me);col.objects.link(o);o.parent=parent;o.location=loc;me.materials.append(mat);me.uv_layers.new(name='Surface_UV')
 if axis=='Y':o.rotation_euler.x=math.pi/2
 mod=o.modifiers.new('Rounded edge','BEVEL');mod.width=min(depth/4,.001);mod.segments=2;return o

def screw(name,parent,x,y,z):
 cyl(name,parent,(x,y,z),.004,.003,steel);box(name+'_slot',parent,(x,y,z+.0016),(.005,.0008,.0003),rubber)

def framed(name,pos,u,w,h,art,mat=pine,glazed=False):
 r=root(name,pos,u);box(name+'_backboard',r,(0,0,.012),(w,h,.018),paper,.002)
 face(name+'_print',r,w-.06,h-.06,.025,art)
 dep=.060 if glazed else .037; rail=.027
 for x in [-1,1]:box(name+f'_side_{x}',r,(x*(w-rail)/2,0,dep/2),(rail,h,dep),mat,.002)
 for y in [-1,1]:box(name+f'_rail_{y}',r,(0,y*(h-rail)/2,dep/2),(w-2*rail,rail,dep),mat,.002)
 for x in [-w*.33,w*.33]:
  box(name+'_mount',r,(x,0,-.003),(.06,.12,.012),steel,.001);screw(name+'_mount_screw',r,x,.035,.007)
 if glazed:
  box(name+'_glass',r,(0,0,.044),(w-.060,h-.060,.002),glass,.0002)
  for x in [-w/2+.04,w/2-.04]:
   for y in [-h/2+.04,h/2-.04]:screw(name+'_retainer',r,x,y,.048)
 layers.append(dict(root=r.name,paper_front=.025,paper_back=.02465,backboard_front=.021,glass_back=.043 if glazed else None,surface_gap_m=.00365));r['display_size_m']=[w,h];r['mount_height_above_floor_m']=pos[2]-4;return r
