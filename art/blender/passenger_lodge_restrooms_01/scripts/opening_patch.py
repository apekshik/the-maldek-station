"""Opening-only patch for a review/integration COPY. Never opens or saves a master file.
Call apply() after loading an approved-source copy. Replaces only the boundary
strips beside the two WC openings and their header undersides, preserving the
original object transforms/material slots and upper wall extents.
"""
import bpy
from mathutils import Vector

def apply():
 changes=[]
 for name,lo,hi,left,right in [('FIT_WC_hall_partition_0_0',8.18,10,0,.022),('FIT_WC_hall_partition_2_0',10.9,12,.022,.022),('FIT_WC_hall_partition_4_0',12.9,13.82,.022,0)]:
  o=bpy.data.objects[name]
  if o.get('PLR_opening_patch'):continue
  # Notch is confined below the recessed header; upper wall stays full-width.
  profile=[(lo+left,0),(hi-right,0),(hi-right,2.226)]
  if right:profile.append((hi,2.226))
  profile += [(hi,3.2),(lo,3.2)]
  if left:profile.append((lo,2.226))
  profile.append((lo+left,2.226))
  # Remove coincident consecutive vertices when a side has no notch.
  clean=[]
  for q in profile:
   if not clean or q!=clean[-1]:clean.append(q)
  profile=clean;N=len(profile)
  v=[o.matrix_world.inverted()@Vector((x-24.1,4-d,z+4)) for d in [13.02,13.2] for x,z in profile]
  faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  me=bpy.data.meshes.new(name+'_PLR_opening_recess');me.from_pydata(v,[],faces);me.update()
  for m in o.data.materials:me.materials.append(m)
  o.data=me;o['PLR_opening_patch']=True
  changes.append(dict(object=name,operation='notch_jamb_boundary_only',local_x=[lo,hi],left_recess=left,right_recess=right,local_depth=[13.02,13.2],local_z=[0,2.226],upper_wall_unchanged=True))
 for name in ['FIT_WC_hall_partition_1_2.2','FIT_WC_hall_partition_3_2.2']:
  o=bpy.data.objects[name]
  if o.get('PLR_opening_patch'):continue
  o.data=o.data.copy()
  for v in o.data.vertices:
   w=o.matrix_world@v.co
   if abs(w.z-6.2)<.0001:w.z+=.026;v.co=o.matrix_world.inverted()@w
  o['PLR_opening_patch']=True;changes.append(dict(object=name,operation='recess_header_underside',world_z=6.2,delta_z=.026))
 return changes
