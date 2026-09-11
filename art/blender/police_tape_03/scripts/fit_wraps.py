"""Fit taut tape to convex bark cross-sections exported from the live tree assets."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'art/unreal_handoff/revision12/police_tape/wrap_fit'
rows=json.loads((OUT/'survey.json').read_text());cache={};results=[]
def hull(points):
    points=sorted(set((round(x,7),round(y,7)) for x,y in points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower=[];upper=[]
    for p in points:
        while len(lower)>1 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper)>1 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]
def section(tris,z):
    graph={}
    for tri in tris:
        if not min(v[2] for v in tri)<=z<=max(v[2] for v in tri):continue
        points=[]
        for a,b in zip(tri,tri[1:]+tri[:1]):
            if (a[2]-z)*(b[2]-z)<0:
                t=(z-a[2])/(b[2]-a[2]);x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
                points.append((round(x,5),round(y,5)))
        if len(points)==2:
            a,b=points;graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
    # Bark UV seams can split otherwise contiguous rings into separate strips.
    points=[p for p in graph if math.hypot(*p)<.45]
    if len(hull(points))<3:
        points.extend((v[0],v[1]) for tri in tris for v in tri if abs(v[2]-z)<.10 and math.hypot(v[0],v[1])<.45)
    assert len(hull(points))>=3,(z,len(points))
    return hull(points)

def ring(poly,clearance):
    cx=sum(x for x,y in poly)/len(poly);cy=sum(y for x,y in poly)/len(poly);result=[]
    for i in range(97):
        a=2*math.pi*i/96;dx,dy=math.cos(a),math.sin(a);hits=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            ex,ey=q[0]-p[0],q[1]-p[1];det=dx*ey-dy*ex
            if abs(det)<1e-9:continue
            px,py=p[0]-cx,p[1]-cy;t=(px*ey-py*ex)/det;u=(px*dy-py*dx)/det
            if t>=0 and 0<=u<=1:hits.append(t)
        assert hits
        # Render-envelope allowance for the simplified exported bark cross-section.
        r=min(hits)+clearance;result.append((cx+dx*r,cy+dy*r))
    return result
for row in rows:
    if row['fbx'] not in cache:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=row['fbx'],use_anim=False)
        tris=[]
        for ob in bpy.context.scene.objects:
            if ob.type!='MESH':continue
            ob.data.calc_loop_triangles();verts=[tuple(ob.matrix_world@v.co) for v in ob.data.vertices]
            tris.extend([[verts[i] for i in t.vertices] for t in ob.data.loop_triangles if 'bark' in ob.data.materials[t.material_index].name.lower()])
        cache[row['fbx']]=tris
    tris=cache[row['fbx']];scale=row['tree_scale'];height=(row['wrap_position'][2]-row['tree_position'][2])/100/scale[2]
    envelope=hull([p for j in range(9) for p in section(tris,height+(-.0381+.0762*j/8)/scale[2])]);clearance=.027 if row['wrap'].startswith('PoliceTape_Wrap_') and row['wrap'].endswith('_2') else .015;low=ring(envelope,clearance);high=low;vs=[];fs=[]
    for i in range(97):
        for j,points in enumerate([low,high]):vs.append((points[i][0]*scale[0],points[i][1]*scale[1],(-.0381 if j==0 else .0381)))
    for i in range(96):a=i*2;fs.append((a,a+2,a+3,a+1))
    bpy.ops.wm.read_factory_settings(use_empty=True);mesh=bpy.data.meshes.new(row['wrap']);mesh.from_pydata(vs,[],fs);mesh.update();uv=mesh.uv_layers.new()
    distances=[0]
    for i in range(1,97):distances.append(distances[-1]+math.dist(vs[i*2],vs[(i-1)*2]))
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(distances[vi//2]/1.2192,vi%2)
    ob=bpy.data.objects.new('SM_'+row['wrap'],mesh);bpy.context.scene.collection.objects.link(ob);ob.select_set(True);bpy.context.view_layer.objects.active=ob
    file=OUT/(ob.name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
    results.append({**row,'fitted_fbx':str(file),'source_height_m':height,'width_m':.0762,'clearance_m':clearance,'xy_bounds_m':[[min(p[k] for p in vs),max(p[k] for p in vs)] for k in [0,1]],'circumference_m':distances[-1],'mid_ring_m':[[(low[i][k]+high[i][k])*.5*scale[k] for k in range(2)] for i in range(96)]})
(OUT/'fitted.json').write_text(json.dumps(results,indent=2));print([(r['wrap'],r['xy_bounds_m']) for r in results])
