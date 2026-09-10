"""Packed CC0 scan maps plus adjustable, authored abandonment layers. Blender-only shader graphs."""
import bpy,json,hashlib
from pathlib import Path

def apply(P,asset):
    # Face-aligned metric UVs: 2 m per source repeat. UVs move with hinged geometry.
    for ob in asset.objects:
        if ob.type!='MESH':continue
        uv=ob.data.uv_layers.new(name='PLR_Metric_2m')
        for face in ob.data.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
            for li in face.loop_indices:
                co=ob.data.vertices[ob.data.loops[li].vertex_index].co
                uv.data[li].uv=(co[axes[0]]/2+.317,co[axes[1]]/2+.173)
    files=json.loads((P/'textures/provenance.json').read_text(encoding='utf-8-sig'))
    for record in files:
        data=(P/'textures'/record['file']).read_bytes()
        assert hashlib.md5(data).hexdigest()==record['md5']
    images={}
    for key in ['diff','rough','metal','nor_gl']:
        im=bpy.data.images.load(str(P/'textures'/('metal_plate_02_'+key+'_2k.jpg')),check_existing=True)
        im.colorspace_settings.name='sRGB' if key=='diff' else 'Non-Color';im.pack();im.filepath='//textures/'+Path(im.filepath).name;images[key]=im
    for name in ['Brushed_chrome','Laminate_petrol','Vitreous_cream','Seat_ivory']:
        mat=bpy.data.materials['PLR_'+name];nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
        def node(kind,label):
            a=nodes.new(kind);a.label=label;a.name=label;return a
        def wire(a,out,b,inp):links.new(a.outputs[out],b.inputs[inp])
        def mathn(op,a,b,label):
            nd=node('ShaderNodeMath',label);nd.operation=op
            if isinstance(a,tuple):wire(a[0],a[1],nd,0)
            else:nd.inputs[0].default_value=a
            if isinstance(b,tuple):wire(b[0],b[1],nd,1)
            else:nd.inputs[1].default_value=b
            return nd
        base=tuple(p.inputs['Base Color'].default_value)
        tex=node('ShaderNodeTexCoord','Stable component coordinates')
        scan=node('ShaderNodeTexImage','CC0 metal scan - roughness / wear variation');scan.image=images['rough'];wire(tex,'UV',scan,'Vector')
        noise=node('ShaderNodeTexNoise','Uneven grime breakup');noise.inputs['Scale'].default_value=17;noise.inputs['Detail'].default_value=4;wire(tex,'Object',noise,'Vector')
        ramp=node('ShaderNodeValToRGB','Patchy dirt distribution');ramp.color_ramp.elements[0].position=.36;ramp.color_ramp.elements[1].position=.70;wire(noise,'Fac',ramp,'Fac')
        strength=node('ShaderNodeValue','Abandonment amount');strength.outputs[0].default_value=.46 if name=='Laminate_petrol' else .09
        mask=mathn('MULTIPLY',(ramp,'Color'),(strength,0),'Adjustable surface dirt')
        if name=='Vitreous_cream':
            attr=node('ShaderNodeAttribute','Basin rim and drain deposits');attr.attribute_name='PLR_Deposit'
            localized=mathn('MULTIPLY',(attr,'Fac'),(ramp,'Color'),'Localized mineral deposits')
            mask=mathn('ADD',(mask,0),(localized,0),'General age plus wet-area deposits')
            mask.use_clamp=True
            fine=node('ShaderNodeTexNoise','Fine mineral speckling');fine.inputs['Scale'].default_value=145;fine.inputs['Detail'].default_value=3;wire(tex,'Object',fine,'Vector')
            mask=mathn('MULTIPLY',(mask,0),(fine,'Fac'),'Broken deposit edges')
        mix=node('ShaderNodeMixRGB','Base finish with accumulated dirt');mix.inputs[1].default_value=base;mix.inputs[2].default_value=(.16,.125,.065,1) if name!='Laminate_petrol' else (.027,.047,.026,1);wire(mask,0,mix,0);wire(mix,0,p,'Base Color')
        rough=node('ShaderNodeMapRange','Variable dulled finish');rough.inputs['To Min'].default_value=.22 if name!='Laminate_petrol' else .36;rough.inputs['To Max'].default_value=.58 if name!='Laminate_petrol' else .73;wire(scan,'Color',rough,'Value');wire(rough,'Result',p,'Roughness')
        if name=='Vitreous_cream':
            dull=mathn('MULTIPLY',(mask,0),.65,'Deposit roughness');dull=mathn('ADD',(dull,0),.17,'Glaze beneath deposits');wire(dull,0,p,'Roughness')
        bump=node('ShaderNodeBump','Microscopic surface irregularities');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00035;wire(noise,'Fac',bump,'Height');wire(bump,'Normal',p,'Normal')
        if name=='Brushed_chrome':
            albedo=node('ShaderNodeTexImage','CC0 metal scan - albedo');albedo.image=images['diff'];wire(tex,'UV',albedo,'Vector')
            mix.inputs[0].default_value=.42
            for link in list(mix.inputs[0].links):links.remove(link)
            wire(albedo,'Color',mix,2)
            met=node('ShaderNodeTexImage','CC0 metal scan - metalness');met.image=images['metal'];wire(tex,'UV',met,'Vector');wire(met,'Color',p,'Metallic')
            normal=node('ShaderNodeTexImage','CC0 metal scan - OpenGL normal');normal.image=images['nor_gl'];wire(tex,'UV',normal,'Vector')
            nm=node('ShaderNodeNormalMap','Restrained pitting');nm.inputs['Strength'].default_value=.22;wire(normal,'Color',nm,'Color');wire(nm,'Normal',p,'Normal')
        # Readable graph columns, retained for art-direction adjustment.
        for i,nd in enumerate(nodes):nd.location=((i%5)*260,(i//5)*-260)
        mat['surface_treatment']='CC0 Poly Haven metal scan maps / authored procedural dirt; bake or recreate for Unreal'
    (P/'material_verification.json').write_text(json.dumps({'packed_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name} for im in images.values()],'uv_mesh_count':sum(o.type=='MESH' and bool(o.data.uv_layers) for o in asset.objects),'source':'https://polyhaven.com/a/metal_plate_02','license':'CC0','source_hashes_verified':True,'procedural_layers':'Blender only; bake/recreate at Unreal integration'},indent=2))
