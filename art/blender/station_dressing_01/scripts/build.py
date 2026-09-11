import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P.parent/'west_services_02/Maldek_Station_West_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.name='Station_Furnished';s.frame_set(1);bpy.context.view_layer.update()
old={o.name:[list(r) for r in o.matrix_world] for o in s.objects};old.pop('FIT_Cleaning_cupboard');bpy.data.objects.remove(bpy.data.objects['FIT_Cleaning_cupboard'],do_unlink=True)
cols={}
for name in ['SD_JANITOR','SD_RESCUE_DRESSING','SD_POWER_DRESSING','SD_REVIEW_ONLY']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);cols[name]=c
c=cols['SD_JANITOR'];records=[]
def mat(n,col,metal=0):
 m=bpy.data.materials.new('SD_'+n);m.diffuse_color=(*col,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=.66;bs.inputs['Metallic'].default_value=metal;return m
pine=mat('Pine',(.33,.23,.14));green=mat('Paint',(.07,.22,.19));cream=mat('Paper',(.72,.68,.55));blue=mat('BottleBlue',(.10,.23,.3));red=mat('Red',(.48,.16,.09));steel=mat('Galvanized',(.36,.4,.41),.6);cloth=mat('Cloth',(.38,.42,.27));rubber=mat('Rubber',(.03,.04,.035))
def mesh(n,v,f,m):
 me=bpy.data.meshes.new('SD_'+n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('SD_'+n,me);c.objects.link(o);me.materials.append(m);return o
def box(n,a,b,m=green,bev=0):
 v=[(x,y,z) for z in [a[2],b[2]] for y in [a[1],b[1]] for x in [a[0],b[0]]];o=mesh(n,v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
 if bev:mo=o.modifiers.new('Soft edges','BEVEL');mo.width=bev;mo.segments=2
 return o
def rod(n,a,b,r,m=steel,N=16):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,0,1)))
 if u.length<.01:u=v.cross(Vector((0,1,0)))
 u.normalize();w=v.cross(u);pts=[p+r*(math.cos(i*math.tau/N)*u+math.sin(i*math.tau/N)*w) for p in [a,b] for i in range(N)];return mesh(n,pts,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m)
def text(n,body,pos,size=.035,face='south',material=cream):
 cu=bpy.data.curves.new('SD_'+n,'FONT');cu.body=body;cu.size=size;cu.extrude=.0004;o=bpy.data.objects.new(cu.name,cu);c.objects.link(o);o.location=pos;o.rotation_euler=(math.pi/2,0,0) if face=='south' else (math.pi/2,0,-math.pi/2);cu.materials.append(material);return o
def bottle(n,x,y,z,h=.23,m=blue):
 rod(n,(x,y,z+.005),(x,y,z+h*.76),.046,m);rod(n+'Neck',(x,y,z+h*.76),(x,y,z+h*.94),.022,m);rod(n+'Cap',(x,y,z+h*.94),(x,y,z+h),.026,cream)
 box(n+'Label',(x-.032,y-.047,z+.07),(x+.032,y-.045,z+.14),cream)
def rack(n,x0,x1,y0,y1,z,levels):
 for x in [x0,x1-.025]:
  for y in [y0,y1-.025]:box(n+'Upright',(x,y,z),(x+.025,y+.025,levels[-1]+.1),green)
 for zz in levels:
  box(n+'Shelf',(x0+.025,y0+.025,zz-.025),(x1-.025,y1-.025,zz),pine)
  box(n+'FrontLip',(x0+.025,y0+.01,zz),(x1-.025,y0+.025,zz+.035),green)
# Janitor cupboard: same 0.5 x 1.0 m footprint, west-facing open storage.
for y in [-8.30,-7.325]:box('JanitorSide',(-10.9,y,4.0),(-10.4,y+.025,6.0),green)
box('JanitorBack',(-10.425,-8.275,4),(-10.4,-7.325,6),green)
box('JanitorDivider',(-10.88,-7.69,4.03),(-10.425,-7.665,5.98),green)
for z in [4.04,4.53,4.98,5.43,5.73]:
 box('JanitorShelf',(-10.875,-8.275,z),(-10.425,-7.69,z+.025),pine)
 # shelf edge numbering faces the aisle
 text('ShelfMark',str(round(z-4,1)),(-10.878,-7.84,z+.03),.025,'west')
box('JanitorTop',(-10.9,-8.3,5.975),(-10.4,-7.3,6),green)
# Supplies stocked above real shelf tops.
for y,z in [(-8.16,4.555),(-7.96,4.555),(-8.14,5.005),(-7.94,5.005)]:bottle('CleaningBottle',-10.62,y,z,.23,blue if z<5 else cream)
for j in range(3):box('FoldedRag',(-10.83,-8.22,5.455+j*.035),(-10.55,-7.94,5.487+j*.035),cloth,.01)
for y in [-8.16,-7.95]:
 rod('PaperRoll',(-10.63,y,5.755),(-10.63,y,5.92),.075,cream)
# Bucket as a closed wall with an open interior.
vs=[];N=24
for r,z in [(.12,4.065),(.14,4.34),(.126,4.34),(.108,4.083)]:
 for i in range(N):vs.append((-10.65+r*math.cos(i*math.tau/N),-8.00+r*math.sin(i*math.tau/N),z))
faces=[]
for ring in range(3):
 for i in range(N):faces.append((ring*N+i,ring*N+(i+1)%N,(ring+1)*N+(i+1)%N,(ring+1)*N+i))
faces += [tuple(reversed(range(N))),tuple(range(3*N,4*N))];mesh('Bucket',vs,faces,steel)
for side in [-1,1]:rod('BucketHandle',(-10.65,-8+side*.14,4.31),(-10.65,-8+side*.07,4.47),.008,steel)
rod('BucketGrip',(-10.65,-8.07,4.47),(-10.65,-7.93,4.47),.013,rubber)
# Narrow tall tool bay keeps handles inside the original footprint.
box('ToolClipRail',(-10.46,-7.64,5.35),(-10.426,-7.36,5.41),steel)
for i,y in enumerate([-7.57,-7.40]):
 rod('MopHandle' if i==0 else 'BroomHandle',(-10.62,y,4.18),(-10.52,y,5.72),.013,pine)
 rod('Clip',(-10.46,y,5.38),(-10.53,y,5.38),.018,rubber)
 if i==0:
  for j in range(7):rod('MopStrand',(-10.68+j*.018,y,4.19),(-10.7+j*.022,y-.01,4.065),.010,cream)
 else:
  box('BroomHead',(-10.76,y-.06,4.10),(-10.47,y+.06,4.17),pine,.008)
  for j in range(12):rod('Bristles',(-10.745+j*.023,y,4.11),(-10.745+j*.023,y,4.045),.008,rubber)
# Small framed cleaning rota above cupboard, inside existing wall footprint.
for yy in [-8.15,-7.59]:box('RotaBracket',(-10.425,yy,6.0),(-10.401,yy+.018,6.46),steel)
box('CleaningRota',(-10.435,-8.2,6.15),(-10.412,-7.52,6.46),cream,.004)
text('RotaText','CLEANING\nCHECK / RESTOCK',(-10.437,-7.57,6.39),.052,'west',green)
# Rescue: north-west wall shelves, separate from heater/radio and stretcher route.
c=cols['SD_RESCUE_DRESSING']
for z in [5.80,6.28]:
 box('RescueWallShelf',(-36.90,4.50,z-.028),(-35.35,4.75,z),pine,.004)
 for x in [-36.78,-35.49]:
  box('ShelfBracketWall',(x,4.72,z-.23),(x+.03,4.75,z-.03),steel)
  rod('ShelfBracket',(x,4.72,z-.20),(x,4.51,z-.035),.011,steel)
for i,x in enumerate([-36.70,-36.27,-35.82]):
 box('MedicalSupplies',(x,4.53,5.8),(x+.28,4.71,6.02),cream,.008)
 text('SupplyLabel',['DRESSINGS','GLOVES','TAPE'][i],(x+.015,4.526,5.88),.029,'south',green)
for i in range(3):
 rod('RolledBlanket',(-36.72+i*.34,4.59,6.373),(-36.72+i*.34,4.70,6.373),.09,cloth)
 rod('BlanketBand',(-36.72+i*.34,4.63,6.373),(-36.72+i*.34,4.66,6.373),.093,cream)
for ob in c.objects:
 ob.location.z += .30
# Emergency power: an open rack on the unused north wall and a small tool board.
c=cols['SD_POWER_DRESSING']
rack('SparesRack',-35.95,-34.55,4.18,4.70,1.2,[1.30,1.85,2.40,2.95])
for z in [1.30,1.85,2.40]:
 for i in range(2):
  x=-35.82+i*.62;box('SparesBox',(x,4.28,z),(x+.48,4.61,z+.27),cream,.01)
  text('BoxLabel',['LAMPS','FUSES','SEALS','FILTERS','CLOTHS','FIXINGS'][int(round((z-1.30)/.55))*2+i],(x+.03,4.275,z+.11),.041,'south',green)
for x in [-35.68,-35.2]:
 rod('FilterTin',(x,4.45,2.95),(x,4.45,3.19),.10,steel)
 rod('FilterCap',(x,4.45,3.19),(x,4.45,3.205),.105,green)
box('ToolBoard',(-34.25,4.704,1.95),(-33.10,4.74,3.05),pine,.008)
for i,x in enumerate([-34.10,-33.87,-33.62,-33.36]):
 rod('ToolHook',(x,4.68,2.93),(x,4.61,2.93),.009,steel)
 box('ToolHandle',(x-.023,4.60,2.40+i*.08),(x+.023,4.64,2.86),steel,.004)
 # Open-ended wrench silhouette from a bridge and two jaws.
 box('ToolHead',(x-.06,4.596,2.85),(x+.06,4.647,2.88),steel,.003)
 for dx in [-.06,.03]:box('ToolJaw',(x+dx,4.596,2.88),(x+dx+.03,4.647,2.94),steel,.003)
text('ToolBoardLabel','RETURN TO RACK',(-34.17,4.697,2.04),.06,'south',cream)
# Record exact object additions, old placeholder removal and immutable base.
bpy.context.view_layer.update();manifest={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'removed':['FIT_Cleaning_cupboard'],'collections':{n:[o.name for o in cc.all_objects] for n,cc in cols.items()},'preserved_transforms':old,'scope':'Janitor cupboard replacement and additive rescue/power dressing. No architecture or live Unreal edits.'}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Station_Furnished.blend'));print('DRESSING COMPLETE',sum(len(cc.objects) for cc in cols.values()))

