"""Local aged paint variation + CC0 roughness. No source material mutation."""
import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'))
col=bpy.data.collections['PLL_Lockers'];texpath=OUT/'textures/PaintedMetal012_1K-JPG_Roughness.jpg'
img=bpy.data.images.load(str(texpath),check_existing=True);img.colorspace_settings.name='Non-Color';img.pack()
def material(k,door=False):
 m=bpy.data.materials.new('PLL_Aged_Petrol_'+str(k)+('_Door' if door else '_Carcass'));m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 def node(t):return n.new(t)
 def mathn(op,a,b):
  q=node('ShaderNodeMath');q.operation=op
  for i,v in enumerate([a,b]):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 out=node('ShaderNodeOutputMaterial');p=node('ShaderNodeBsdfPrincipled');l.new(p.outputs['BSDF'],out.inputs[0]);p.inputs['Metallic'].default_value=.32
 coord=node('ShaderNodeTexCoord');sep=node('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0]);comb=node('ShaderNodeCombineXYZ');l.new(mathn('ADD',sep.outputs['X'],k*.293),comb.inputs['X']);l.new(mathn('ADD',mathn('MULTIPLY',sep.outputs['Z'],.70),k*.371),comb.inputs['Y'])
 tex=node('ShaderNodeTexImage');tex.image=img;tex.extension='REPEAT';l.new(comb.outputs[0],tex.inputs['Vector'])
 noise=node('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95;noise.inputs['Detail'].default_value=3;l.new(coord.outputs['Object'],noise.inputs['Vector'])
 ramp=node('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[0].color=(.055+k*.002,.125+k*.003,.118+k*.003,1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.11+k*.002,.205+k*.003,.183+k*.003,1);l.new(tex.outputs['Color'],ramp.inputs[0])
 color=ramp.outputs['Color']
 if door:
  # Restrict abrasions to edges; several units use different map offsets.
  edge=mathn('GREATER_THAN',mathn('ABSOLUTE',sep.outputs['X'],0),.130)
  bottom=mathn('LESS_THAN',sep.outputs['Z'],-.56)
  chip=mathn('MULTIPLY',edge,mathn('GREATER_THAN',noise.outputs['Fac'],.62))
  mix=node('ShaderNodeMixRGB');l.new(chip,mix.inputs[0]);l.new(color,mix.inputs[1]);mix.inputs[2].default_value=(.14,.12,.085,1);color=mix.outputs[0]
  grime=node('ShaderNodeMixRGB');l.new(mathn('MULTIPLY',bottom,mathn('MULTIPLY',tex.outputs['Color'],.48)),grime.inputs[0]);l.new(color,grime.inputs[1]);grime.inputs[2].default_value=(.043,.057,.045,1);color=grime.outputs[0]
 l.new(color,p.inputs['Base Color']);l.new(mathn('ADD',mathn('MULTIPLY',tex.outputs['Color'],.32),.4),p.inputs['Roughness'])
 bump=node('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.00012;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 m['integration']='Blender procedural + packed CC0 image; bake for engine';return m
body=material(0);variants=[material(k,True) for k in range(3)];shared={}
for o in col.objects:
 if o.type!='MESH':continue
 if o.name.endswith('_Door_Sheet'):
  k=(int(o.name[4:6])-1)%3
  if k not in shared:shared[k]=o.data.copy();shared[k].materials.clear();shared[k].materials.append(variants[k])
  o.data=shared[k]
 elif o.data.materials and o.data.materials[0].name=='VF06_Petrol_paint':o.data.materials[0]=body
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Lockers.blend'),compress=True)
bpy.data.libraries.write(str(OUT/'PLL_Asset_Only.blend'),{col},fake_user=True,compress=True)
m=json.loads((OUT/'replacement_manifest.json').read_text())
for entry in m['objects']:
 o=bpy.data.objects[entry['name']]
 if o.type in ['MESH','FONT']:entry['material_slots']=[x.name for x in o.data.materials]
m['instance_strategy']='Three shared door mesh/material variants, four lockers each; repeated panels share mesh data. Individually named door parents, number curves and keyed lock parts.'
m['weathering']='CC0 roughness-map variation, restrained edge abrasion, lower-door grime; procedural micro-bump. No geometry displacement. Source materials unchanged.'
(OUT/'replacement_manifest.json').write_text(json.dumps(m,indent=2))
(OUT/'textures/sources.json').write_text(json.dumps({'asset':'Painted Metal 012','author':'ambientCG / Lennart Demes','source':'https://ambientcg.com/view?id=PaintedMetal012','download':'https://ambientcg.com/get?file=PaintedMetal012_1K-JPG.zip','license':'CC0 1.0','license_url':'https://docs.ambientcg.com/license/','retained_file':texpath.name,'sha256':hashlib.sha256(texpath.read_bytes()).hexdigest(),'use':'Non-color roughness and subtle painted-surface color variation; packed into both blends. Source color/rust maps are not used.'},indent=2))
