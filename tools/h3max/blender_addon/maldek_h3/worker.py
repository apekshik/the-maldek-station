# SPDX-License-Identifier: GPL-3.0-or-later
"""Runs in a separate Blender process. Never accesses the interactive session."""
import sys,json,hashlib,subprocess,traceback
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
import transport

folder=Path(sys.argv[sys.argv.index('--')+1]);cfg=json.loads((folder/'settings.json').read_text())
state=folder/'status.json'
def status(stage,**extra):core.save(state,dict(stage=stage,**extra))
try:
    status('preparing')
    s=bpy.context.scene
    if not s.camera:raise ValueError('Choose a camera or Use Current View first')
    s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8;s.eevee.use_raytracing=False
    s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.use_sequencer=False;s.render.use_compositing=False
    # Neutral capture keeps visibility useful; H3 mood is controlled by the panel.
    s.view_settings.exposure=0
    if s.world and s.world.use_nodes:
        for n in s.world.node_tree.nodes:
            if n.type=='BACKGROUND':n.inputs['Strength'].default_value=.5
    sun=bpy.data.objects.get('Overcast_Sun')
    if sun:sun.data.energy=1.5
    print('WORKER lighting ready',flush=True)
    atmosphere=bpy.data.collections.get('17_Atmosphere')
    if atmosphere:
        for o in atmosphere.all_objects:o.hide_render=True
    print('WORKER atmosphere ready',flush=True)
    for layer in s.view_layers:layer.use=layer.name==cfg['view_layer']
    bpy.context.window.view_layer=s.view_layers[cfg['view_layer']]
    print('WORKER layer ready',flush=True)
    cam=s.camera
    if cfg['mode'] in ('PAN','DOLLY'):
        cam.animation_data_clear();cam.constraints.clear()
        cam.parent=None;cam.matrix_world=__import__('mathutils').Matrix(cfg['camera_matrix'])
        cam.keyframe_insert(data_path='location',frame=1)
        local_axis=Vector((1,0,0) if cfg['mode']=='PAN' else (0,0,-1))
        cam.location+=cam.matrix_world.to_quaternion()@local_axis*cfg['distance']
        cam.keyframe_insert(data_path='location',frame=120)
    frames=folder/'frames';frames.mkdir()
    count=1 if cfg['mode']=='STILL' else 120
    for i in range(count):
        frame=cfg['current_frame'] if cfg['mode']=='STILL' else (round(cfg['frame_start']+(cfg['frame_end']-cfg['frame_start'])*i/119) if cfg['mode']=='ANIMATION' else i+1)
        s.frame_set(frame);s.render.filepath=str(frames/f'{i+1:04}.png')
        status('capturing',frame=i+1,total=count)
        bpy.ops.render.render(write_still=True,layer=cfg['view_layer'])
    source=frames/'0001.png'
    filtering='format=gray,gblur=sigma=1.2,edgedetect=low=0.08:high=0.2,negate'
    if count>1:
        source=folder/'guide.mp4'
        cmd=[cfg['ffmpeg'],'-y','-v','error','-framerate','24','-i',str(frames/'%04d.png')]
        if cfg['guide']=='LINES':cmd+=['-vf',filtering]
        subprocess.run(cmd+['-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(source)],check=True)
    elif cfg['guide']=='LINES':
        source=folder/'guide.png'
        subprocess.run([cfg['ffmpeg'],'-y','-v','error','-i',str(frames/'0001.png'),'-vf',filtering,'-frames:v','1',str(source)],check=True)
    if not cfg['generate']:
        status('complete',path=str(source),label='Guide only — no API call')
    else:
        key=transport.load_key(cfg['key_file'])
        payload=dict(prompt=core.prompt(cfg),duration=5,resolution=cfg['resolution'],seed=cfg['seed'],
                     aspect_ratio='16:9',prompt_expansion_mode='quality',enable_safety_checker=True,sync_mode=False)
        payload['reference_image_urls' if count==1 else 'reference_video_urls']=[transport.uri(source)]
        status('generating')
        summary=dict(prompt=payload['prompt'],source_guide=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),settings=core.values(type('Settings',(),cfg)()))
        result=transport.generate(payload,summary,key,folder/'api')
        # Keep provider original; present a silent five-second review in Blender.
        review=folder/'preview.mp4'
        subprocess.run([cfg['ffmpeg'],'-y','-v','error','-i',str(result),'-t','5','-an','-c:v','copy',str(review)],check=True)
        status('complete',path=str(review),label='H3 preview')
except Exception as error:
    status('error',message=(str(error) if isinstance(error,(ValueError,RuntimeError)) else type(error).__name__+' — inspect worker.log'))
    raise
